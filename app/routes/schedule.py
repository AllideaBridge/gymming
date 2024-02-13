from flask_restx import Namespace, Resource, fields
from sqlalchemy import func
from sqlalchemy.sql.functions import coalesce

from app.models.Trainer import Trainer
from app.models.Center import Center
from app.models.TrainingUser import TrainingUser
from app.models.Schedule import Schedule
from database import db

ns_schedule = Namespace('schedules', description='Schedules related operations')

# API 모델 정의
user_schedule_model = ns_schedule.model('UserSchedule', {
    'trainer_name': fields.String,
    'lesson_name': fields.String,
    'center_name': fields.String,
    'center_location': fields.String,
    'schedule_start_time': fields.DateTime,
    'schedule_id': fields.Integer
})


# 회원의 한달 중 스케쥴이 있는 날짜 조회.
@ns_schedule.route('/<int:user_id>/<int:year>/<int:month>')
class UserMonthScheduleList(Resource):
    def get(self, user_id, year, month):
        schedules = db.session.query(func.distinct(func.date(Schedule.schedule_start_time))).join(TrainingUser).filter(
            TrainingUser.user_id == user_id,
            db.extract('year', Schedule.schedule_start_time) == year,
            db.extract('month', Schedule.schedule_start_time) == month).all()

        scheduled_dates = [schedule[0].strftime('%Y-%m-%d') for schedule in schedules]

        return sorted(scheduled_dates)


@ns_schedule.route('/<int:user_id>/<int:year>/<int:month>/<int:day>')
class UserDayScheduleList(Resource):
    @ns_schedule.marshal_with(user_schedule_model)
    def get(self, user_id, year, month, day):
        schedules = db.session.query(
            Trainer.trainer_name,
            coalesce(Trainer.lesson_name, '').label('lesson_name'),
            coalesce(Center.center_name, '').label('center_name'),
            coalesce(Center.center_location, '').label('center_location'),
            Schedule.schedule_start_time,
            Schedule.schedule_id
        ).join(TrainingUser, TrainingUser.training_user_id == Schedule.training_user_id) \
            .join(Trainer, TrainingUser.trainer_id == Trainer.trainer_id) \
            .outerjoin(Center, Trainer.center_id == Center.center_id) \
            .filter(TrainingUser.user_id == user_id,
                    func.year(Schedule.schedule_start_time) == year,
                    func.month(Schedule.schedule_start_time) == month,
                    func.day(Schedule.schedule_start_time) == day) \
            .all()

        return schedules
