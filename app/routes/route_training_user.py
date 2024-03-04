from flask_restx import Resource, fields, Namespace

from app.models.model_TrainingUser import TrainingUser
from app.models.model_Users import Users
from database import db

ns_training_user = Namespace('training-user', description='사용자 관련 작업')

training_user_model = ns_training_user.model('TrainingUser', {
    'trainer_id': fields.Integer(required=True, description='트레이너 ID'),
    'user_name': fields.String(required=True, description='사용자 이름'),
    'user_phone_number': fields.String(required=True, description='사용자 전화번호'),
    'lesson_total_count': fields.Integer(required=True, description='총 수업 횟수'),
    'exercise_days': fields.String(description='운동 일정'),
    'special_notes': fields.String(description='특별 사항')
})


@ns_training_user.route('/register')
class UserRegister(Resource):
    @ns_training_user.expect(training_user_model)
    def post(self):
        data = ns_training_user.payload
        user = Users.query.filter_by(user_name=data['user_name'], user_phone_number=data['user_phone_number']).first()

        if not user:
            return {'message': '유저가 존재하지 않습니다.'}, 404

        training_user = TrainingUser(
            trainer_id=data['trainer_id'],
            user_id=user.user_id,
            lesson_total_count=data['lesson_total_count'],
            lesson_current_count=0,
            exercise_days=data['exercise_days'],
            special_notes=data['special_notes']
        )

        db.session.add(training_user)
        db.session.commit()

        return {'message': '새로운 회원이 등록되었습니다.'}, 200
