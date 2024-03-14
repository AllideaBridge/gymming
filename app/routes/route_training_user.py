from datetime import datetime

from flask import request
from flask_restx import Resource, fields, Namespace

from app.models.model_Trainer import Trainer
from app.models.model_Center import Center
from app.models.model_Schedule import Schedule
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


@ns_training_user.route('/user')
class TrainingUserUser(Resource):
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

    def put(self):
        data = ns_training_user.payload
        training_user_id = data['training_user_id']
        lesson_total_count = data['lesson_total_count']
        lesson_current_count = data['lesson_current_count']

        training_user = TrainingUser.query.filter_by(training_user_id=training_user_id).first()

        if training_user:
            # 레코드의 lesson_total_count, lesson_current_count 업데이트
            training_user.lesson_total_count = lesson_total_count
            training_user.lesson_current_count = lesson_current_count

            # 데이터베이스 세션을 통해 변경 사항 커밋
            db.session.commit()

            return {'message': 'TrainingUser updated successfully'}, 200
        else:
            return {'message': 'TrainingUser not found'}, 404

    def delete(self):
        data = ns_training_user.payload
        training_user_id = data['training_user_id']

        training_user = TrainingUser.query.filter_by(training_user_id=training_user_id).first()

        if training_user:
            # 레코드의 lesson_total_count, lesson_current_count 업데이트
            training_user.training_user_delete_flag = True

            # 데이터베이스 세션을 통해 변경 사항 커밋
            db.session.commit()

            return {'message': 'TrainingUser updated successfully'}, 200
        else:
            return {'message': 'TrainingUser not found'}, 404


@ns_training_user.route('/month-schedules')
class TrainingUserSchedules(Resource):
    def get(self):
        training_user_id = request.args.get('training_user_id', type=int)
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)

        if not training_user_id:
            return {"message": "training_user_id는 필수 입력값이며, 정수여야 합니다."}, 400
        if not year or year < 1:
            return {"message": "year는 필수 입력값이며, 양의 정수여야 합니다."}, 400
        if not month or month < 1 or month > 12:
            return {"message": "month는 필수 입력값이며, 1부터 12 사이의 정수여야 합니다."}, 400

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        schedules = Schedule.query.filter(
            Schedule.training_user_id == training_user_id,
            Schedule.schedule_start_time >= start_date,
            Schedule.schedule_start_time < end_date
        ).all()

        return {
            "schedules": [
                {"schedule_id": schedule.schedule_id, "day": schedule.schedule_start_time.day}
                for schedule in schedules
            ]
        }


@ns_training_user.route('/schedule/<int:schedule_id>')
class TrainingUserSchedule(Resource):
    def get(self, schedule_id):
        result = db.session.query(
            Schedule.schedule_start_time,
            Schedule.schedule_status,
            Center.center_location,
            Center.center_name
        ).join(TrainingUser, TrainingUser.training_user_id == Schedule.training_user_id
               ).join(Trainer, Trainer.trainer_id == TrainingUser.trainer_id
                      ).outerjoin(Center, Center.center_id == Trainer.center_id  # outerjoin 사용
                                  ).filter(Schedule.schedule_id == schedule_id).first()

        if not result:
            return {"message": "해당 schedule_id를 가진 스케줄이 존재하지 않습니다."}, 404

        schedule_start_time, schedule_status, center_location, center_name = result

        # Center 정보가 없는 경우 None 또는 적절한 대체 값을 반환
        return {
            "schedule_start_time": schedule_start_time.strftime('%Y-%m-%d') if schedule_start_time else None,
            "schedule_status": schedule_status,
            "center_location": center_location if center_location else "정보 없음",
            "center_name": center_name if center_name else "정보 없음"
        }
