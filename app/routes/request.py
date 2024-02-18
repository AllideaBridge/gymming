from flask_restx import Namespace, fields, Resource
from sqlalchemy import and_

from app.models.Users import Users
from app.models.Request import Request
from app.models.TrainingUser import TrainingUser
from app.models.Schedule import Schedule
from database import db

ns_request = Namespace('request', description='Request related operations')

request_model = ns_request.model('RequestModel', {
    'schedule_id': fields.Integer(required=True, description='스케줄 ID'),
    'request_from': fields.String(required=True, description='요청자'),
    'request_type': fields.String(required=True, description='요청 타입'),
    'request_description': fields.String(required=True, description='요청 설명'),
    'request_time': fields.DateTime(required=True, description='요청 시간')
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
            .join(Schedule, and_(Request.schedule_id == Schedule.schedule_id, Request.request_from == 'user')) \
            .join(TrainingUser, and_(Schedule.training_user_id == TrainingUser.training_user_id,
                                     TrainingUser.trainer_id == trainer_id)) \
            .join(Users, Users.user_id == TrainingUser.user_id) \
            .all()

        return [{'user_name': r[0], 'request_type': r[1],
                 'request_time': r[2].strftime('%Y-%m-%d %H:%M:%S') if r[2] else "",
                 'created_at': r[3].strftime('%Y-%m-%d %H:%M:%S'),
                 'schedule_start_time': r[4].strftime('%Y-%m-%d %H:%M:%S'),
                 'request_id': r[5]} for r in results]
