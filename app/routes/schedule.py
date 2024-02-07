import calendar
from datetime import datetime

from flask import jsonify
from flask_restx import Namespace, Resource, fields
from sqlalchemy import func

from app.models.Users import Users
from app.models.Trainer import Trainer
from app.models.Center import Center
from app.models.TrainingUser import TrainingUser
from app.models.Schedule import Schedule
from database import db

ns_schedule = Namespace('schedules', description='Schedules related operations')

schedule_model = ns_schedule.model('Schedule', {
    'schedule_id': fields.Integer(readonly=True, description='The schedule unique identifier'),
    'lesson_id': fields.Integer(required=True, description='The lesson id'),
    'schedule_start_time': fields.DateTime(required=True, description='Start time of the schedule'),
    'schedule_end_time': fields.DateTime(required=True, description='End time of the schedule'),
    'schedule_status': fields.String(description='Status of the schedule')
})

lesson_schedule_model = ns_schedule.model('LessonSchedule', {
    'schedule_start_time': fields.DateTime,
    'lesson_name': fields.String,
    'trainer_name': fields.String,
    'center_name': fields.String,
    'center_location': fields.String
})


@ns_schedule.route('/trainer/<int:trainer_id>')
class TrainerSchedule(Resource):
    @ns_schedule.marshal_list_with(schedule_model)
    def get(self, trainer_id):
        # 트레이너의 스케쥴 조회
        schedules = Schedule.query.filter_by(trainer_id=trainer_id).all()
        return schedules

    @ns_schedule.expect(schedule_model)
    @ns_schedule.marshal_with(schedule_model)
    def post(self):
        # todo : 트레이너, 회원이 요청 시간에 스케쥴이 없는지 먼저 확인하기.

        # 트레이너의 일정 추가
        data = ns_schedule.payload
        schedule = Schedule(
            schedule_id=data['schedule_id'],
            lesson_id=data['lesson_id'],
            schedule_start_time=data['schedule_start_time'],
            schedule_end_time=data['schedule_end_time'],
            schedule_status=data['schedule_status']
        )
        db.session.add(schedule)
        db.session.commit()
        return schedule, 201


# 회원의 한달 중 스케쥴이 있는 날짜 조회.
@ns_schedule.route('/<int:user_id>/<int:year>/<int:month>')
class UserScheduleList(Resource):
    def get(self, user_id, year, month):
        schedules = db.session.query(func.distinct(func.date(Schedule.schedule_start_time))).join(TrainingUser).filter(
            TrainingUser.user_id == user_id,
            db.extract('year', Schedule.schedule_start_time) == year,
            db.extract('month', Schedule.schedule_start_time) == month).all()

        scheduled_dates = [schedule[0].strftime('%Y-%m-%d') for schedule in schedules]

        return sorted(scheduled_dates)
#
#
# # 회원의 특정 날의 수업 & 스케쥴 조회.
# @ns_schedule.route('/<int:user_id>/<int:year>/<int:month>/<int:day>')
# class LessonSchedule(Resource):
#     @ns_schedule.marshal_list_with(lesson_schedule_model)
#     def get(self, user_id, year, month, day):
#         # 주어진 파라미터로부터 날짜 구성
#         target_date = datetime(year, month, day)
#         # 지정된 사용자와 날짜에 대한 일정 검색
#         schedules = Schedule.query.join(Lesson).join(Trainer).join(Center).filter(
#             Lesson.user_id == user_id,
#             db.func.date(Schedule.schedule_start_time) == target_date.date()
#         ).with_entities(Schedule.schedule_start_time, Lesson.lesson_name, Trainer.trainer_name, Center.center_name,
#                         Center.center_location).all()
#
#         return schedules
# # 시작 시간, 수업 이름, 트레이너 이름, 센터 이름, 센터 위치
