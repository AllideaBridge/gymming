from flask_restx import Namespace, fields, Resource
from sqlalchemy import and_, func, literal_column
from datetime import datetime

from app.common.Constants import REQUEST_FROM_USER, REQUEST_STATUS_WAITING, REQUEST_STATUS_REJECTED, \
    REQUEST_TYPE_CANCEL, REQUEST_STATUS_APPROVED, SCHEDULE_CANCELLED, REQUEST_TYPE_MODIFY, SCHEDULE_MODIFIED, \
    SCHEDULE_SCHEDULED
from app.models.model_Users import Users
from app.models.model_Trainer import Trainer
from app.models.model_Request import Request
from app.models.model_TrainingUser import TrainingUser
from app.models.model_Schedule import Schedule
from database import db

ns_request = Namespace('request', description='Request related operations')

request_model = ns_request.model('RequestModel', {
    'schedule_id': fields.Integer(required=True, description='스케줄 ID'),
    'request_from': fields.String(required=True, description='요청자'),
    'request_type': fields.String(required=True, description='요청 타입'),
    'request_description': fields.String(required=True, description='요청 설명'),
    'request_time': fields.DateTime(required=True, description='요청 시간')
})

request_approve_model = ns_request.model("RequestApproveModel", {
    'request_id': fields.Integer(required=True, description='요청 ID'),
    'request_type': fields.String(required=True, description='요청 타입'),
    'request_time': fields.String(description='요청 시간')
})


@ns_request.route('')
class RequestResource(Resource):
    @ns_request.expect(request_model)
    def post(self):
        data = ns_request.payload
        new_request = Request(
            schedule_id=data['schedule_id'],
            request_from=data['request_from'],
            request_type=data['request_type'],
            request_description=data['request_description'],
            request_time=data['request_time']
        )
        db.session.add(new_request)  # 새로운 요청 객체를 데이터베이스 세션에 추가
        db.session.commit()  # 변경 사항을 데이터베이스에 커밋
        return {'message': '새로운 요청이 성공적으로 생성되었습니다.'}, 201


@ns_request.route('/trainer/<int:trainer_id>')
class TrainerRequestListResource(Resource):
    def get(self, trainer_id):
        results = db.session.query(Users.user_name, Request.request_type, Request.request_time, Request.created_at,
                                   Schedule.schedule_start_time, Request.request_id) \
            .join(Schedule, and_(Request.schedule_id == Schedule.schedule_id, Request.request_from == REQUEST_FROM_USER,
                                 Request.request_status == REQUEST_STATUS_WAITING)) \
            .join(TrainingUser, and_(Schedule.training_user_id == TrainingUser.training_user_id,
                                     TrainingUser.trainer_id == trainer_id)) \
            .join(Users, Users.user_id == TrainingUser.user_id) \
            .all()

        return [{'user_name': r[0], 'request_type': r[1],
                 'request_time': r[2].strftime('%Y-%m-%d %H:%M:%S') if r[2] else "",
                 'created_at': r[3].strftime('%Y-%m-%d %H:%M:%S'),
                 'schedule_start_time': r[4].strftime('%Y-%m-%d %H:%M:%S'),
                 'request_id': r[5]} for r in results]


@ns_request.route('/<int:request_id>/details')
class RequestResource(Resource):
    def get(self, request_id):
        request = db.session.query(Request.request_id, Request.request_description) \
            .filter(Request.request_id == request_id) \
            .first()

        if not request:
            return {'error': 'request not found'}, 404

        return {"request_id": request[0], "request_description": request[1]}


@ns_request.route('/<int:request_id>/reject')
class RequestRejectResource(Resource):
    def patch(self, request_id):
        # todo : 거절 사유 입력
        request_record = Request.query.filter_by(request_id=request_id).first()

        if request_record:
            request_record.request_status = REQUEST_STATUS_REJECTED
            db.session.commit()
            return {'request_id': request_record.request_id, 'request_status': REQUEST_STATUS_REJECTED}, 200
        else:
            return {'message': 'Request not found'}, 404


@ns_request.route('/approve')
class RequestApproveResource(Resource):
    @ns_request.expect(request_approve_model)
    def post(self):
        try:
            data = ns_request.payload
            request_type = data['request_type']
            request_id = data['request_id']

            if request_type != REQUEST_TYPE_MODIFY and request_type != REQUEST_TYPE_CANCEL:
                return {'message': '유효하지 않은 파라미터'}, 400

            request_record = Request.query.filter_by(request_id=request_id).first()
            if not request_record:
                return {'message': 'Request not found'}, 404

            if request_record.request_status != REQUEST_STATUS_WAITING:
                return {'message': 'Invalid Request Status'}, 400

            request_record.request_status = REQUEST_STATUS_APPROVED

            schedule_record = Schedule.query.filter_by(schedule_id=request_record.schedule_id).first()
            if not schedule_record:
                return {'message': 'Schedule not found'}, 404

            if request_type == REQUEST_TYPE_CANCEL:
                schedule_record.schedule_status = SCHEDULE_CANCELLED

            if request_type == REQUEST_TYPE_MODIFY:
                training_user = TrainingUser.query.filter_by(training_user_id=schedule_record.training_user_id).first()
                trainer_id = training_user.trainer_id
                request_time = data['request_time'] if 'request_time' in data else None
                if not request_time:
                    return {'message': 'Request time is missing'}, 400

                conflict_schedule = db.session.query(Schedule). \
                    join(TrainingUser, and_(TrainingUser.training_user_id == Schedule.training_user_id,
                                            Schedule.schedule_status == SCHEDULE_SCHEDULED)). \
                    join(Trainer, and_(Trainer.trainer_id == TrainingUser.trainer_id,
                                       Trainer.trainer_id == trainer_id)). \
                    filter(func.abs(func.timestampdiff(literal_column('MINUTE'), Schedule.schedule_start_time,
                                                       request_time)) < Trainer.lesson_minutes). \
                    first()

                if conflict_schedule:
                    # 충돌하는 스케줄이 있는 경우
                    return {'message': 'New schedule conflicts with existing schedules of the trainer'}, 400

                schedule_record.schedule_status = SCHEDULE_MODIFIED
                new_schedule = Schedule(
                    training_user_id=schedule_record.training_user_id,
                    schedule_start_time=request_time,
                    schedule_status=SCHEDULE_SCHEDULED
                )
                db.session.add(new_schedule)

            db.session.commit()
            return {'message': 'Update successful'}, 200

        except Exception as e:
            print(e)
