from flask_restx import Namespace, fields, Resource, reqparse
from sqlalchemy import and_, func, literal_column
from datetime import datetime

from app.common.Constants import REQUEST_FROM_USER, REQUEST_STATUS_WAITING, REQUEST_STATUS_REJECTED, \
    REQUEST_TYPE_CANCEL, REQUEST_STATUS_APPROVED, SCHEDULE_CANCELLED, REQUEST_TYPE_MODIFY, SCHEDULE_MODIFIED, \
    SCHEDULE_SCHEDULED, DATETIMEFORMAT
from app.models.model_Users import Users
from app.models.model_Trainer import Trainer
from app.models.model_Request import Request
from app.models.model_TrainingUser import TrainingUser
from app.models.model_Schedule import Schedule
from database import db

ns_request = Namespace('request', description='Request related operations')

# 요청 생성 모델 정의
request_model = ns_request.model('RequestModel', {
    'schedule_id': fields.Integer(required=True, description='스케줄 ID'),
    'request_from': fields.String(required=True, description='요청자'),
    'request_type': fields.String(required=True, description='요청 타입'),
    'request_description': fields.String(required=True, description='요청 설명'),
    'request_time': fields.DateTime(required=True, description='요청 시간')
})

# 요청 승인 모델 정의
request_approve_model = ns_request.model("RequestApproveModel", {
    'request_id': fields.Integer(required=True, description='요청 ID'),
    'request_type': fields.String(required=True, description='요청 타입'),
    'request_time': fields.String(description='요청 시간')
})

# 요청 거절 모델 정의
request_reject_model = ns_request.model('RequestRejectModel', {
    'request_reject_reason': fields.String(required=True, description='요청 거절 사유')
})


@ns_request.route('')
class RequestResource(Resource):
    @ns_request.expect(request_model)
    @ns_request.doc(description='유저 또는 트레이너가 요청시 요청을 생성합니다.',
                    params={'schedule_id': '스케쥴 id',
                            'request_from': 'USER or TRAINER',
                            'request_type': 'CANCEL or MODIFY',
                            'request_description': '요청 내용',
                            'request_time': '2024-01-10 12:30:00(%Y-%m-%d %H:%M:%S)'
                            })
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


parser = reqparse.RequestParser()
parser.add_argument('trainer_id', type=int, required=True, help='트레이너 ID')
parser.add_argument('request_status', required=True, action='split',
                    help='요청 상태 (REQUEST_STATUS_WAITING, REQUEST_STATUS_APPROVED, REQUEST_STATUS_REJECTED)')


@ns_request.route('/trainer')
class TrainerRequestListResource(Resource):
    @ns_request.doc(description='트레이너에게 온 요청리스트를 조회합니다.',
                    params={
                        'trainer_id': '트레이너 id',
                        'request_status': 'WAITING or APPROVED or REJECTED'
                    })
    def get(self):
        args = parser.parse_args()
        trainer_id = args['trainer_id']  # 쿼리 파라미터에서 트레이너 ID 추출
        request_status = args['request_status']  # 쿼리 파라미터에서 요청 상태 추출

        # 요청 상태에 따른 조건 분기
        if REQUEST_STATUS_WAITING in request_status and len(request_status) == 1:
            status_condition = Request.request_status == REQUEST_STATUS_WAITING
        elif REQUEST_STATUS_APPROVED in request_status and REQUEST_STATUS_REJECTED in request_status and len(
                request_status) == 2:
            status_condition = Request.request_status.in_([REQUEST_STATUS_APPROVED, REQUEST_STATUS_REJECTED])
        else:
            return {'message': 'Invalid Request Status'}, 400

        results = db.session.query(Users.user_name, Request.request_type, Request.request_time, Request.created_at,
                                   Schedule.schedule_start_time, Request.request_id, Request.request_status) \
            .join(Schedule, and_(Request.schedule_id == Schedule.schedule_id, Request.request_from == REQUEST_FROM_USER,
                                 status_condition)) \
            .join(TrainingUser, and_(Schedule.training_user_id == TrainingUser.training_user_id,
                                     TrainingUser.trainer_id == trainer_id)) \
            .join(Users, Users.user_id == TrainingUser.user_id) \
            .all()

        return [{'user_name': r[0], 'request_type': r[1],
                 'request_time': r[2].strftime(DATETIMEFORMAT) if r[2] else "",
                 'created_at': r[3].strftime(DATETIMEFORMAT),
                 'schedule_start_time': r[4].strftime(DATETIMEFORMAT),
                 'request_id': r[5], 'request_status': r[6]} for r in results]


@ns_request.route('/<int:request_id>/details')
class RequestResource(Resource):
    @ns_request.doc(description='한 요청에 대한 상세조회를 합니다.',
                    params={
                        'request_id': '요청 id'
                    })
    def get(self, request_id):
        request = db.session.query(Request.request_id, Request.request_description) \
            .filter(Request.request_id == request_id) \
            .first()

        if not request:
            return {'error': 'request not found'}, 404

        return {"request_id": request[0], "request_description": request[1]}


@ns_request.route('/reject')
class RequestRejectResource(Resource):
    @ns_request.expect(request_reject_model)
    @ns_request.doc(description='요청을 생성합니다',
                    params={
                        'request_id': '요청 id',
                        'request_reject_reason': '요청 거절 사유'
                    })
    def put(self):
        data = ns_request.payload  # 요청 본문에서 데이터 추출
        request_id = data.get('request_id')
        request_reject_reason = data.get('request_reject_reason')  # 거절 사유 추출

        request_record = Request.query.filter_by(request_id=request_id).first()
        if not request_record:
            return {'message': '요청을 찾을 수 없습니다.'}, 404

        request_record.request_status = REQUEST_STATUS_REJECTED  # 요청 상태를 '거절됨'으로 변경
        request_record.request_reject_reason = request_reject_reason  # 거절 사유를 데이터베이스에 업데이트

        db.session.commit()  # 변경 사항을 데이터베이스에 커밋
        return {'message': '요청이 성공적으로 거절되었습니다.', 'request_reject_reason': request_reject_reason}, 200


@ns_request.route('/approve')
class RequestApproveResource(Resource):
    @ns_request.expect(request_approve_model)
    @ns_request.doc(description='요청을 승인합니다.',
                    params={
                        'request_id': '요청 id',
                        'request_type': 'CANCEL or MODIFY'
                    })
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
                request_time = request_record.request_time
                if not request_time:
                    return {'message': 'Request time is missing'}, 400

                conflict_schedule = Trainer.conflict_trainer_schedule(trainer_id, request_time)

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
