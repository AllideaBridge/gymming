from calendar import monthrange
from datetime import datetime, timedelta, date

from flask import jsonify
from flask_restx import Namespace, Resource, fields
from sqlalchemy import extract, func

from app.models.Trainer import Trainer
from app.models.TrainerAvailability import TrainerAvailability
from app.models.TrainingUser import TrainingUser
from app.models.Schedule import Schedule
from database import db

ns_trainer_schedule = Namespace('trainer_schedule', description='Trainer Schedule API')


# 입력 받은 year, month중 트레이너의 근무 스케쥴이 꽉 차지 않은 날짜 배열을 리턴한다.
@ns_trainer_schedule.route('/<int:trainer_id>/<int:year>/<int:month>')
class TrainerMonthSchedule(Resource):
    def get(self, trainer_id, year, month):
        # 1단계: 트레이너의 전체 가능 요일 조회
        available_week_days = db.session.query(
            TrainerAvailability.week_day
        ).filter_by(
            trainer_id=trainer_id
        ).all()

        if not available_week_days:
            return []

        available_week_days = set([week_day for week_day, in available_week_days])

        # 2단계: 해당 월의 모든 날짜를 순회하며 "근무 가능 날짜" 목록 생성
        available_dates = set()
        num_days = monthrange(year, month)[1]
        for day in range(1, num_days + 1):
            date = datetime(year, month, day)
            if date.weekday() in available_week_days:
                available_dates.add(date.strftime('%Y-%m-%d'))

        # 3단계: 조건을 충족 하는 날짜 조회 및 "근무 가능 날짜"에서 제외
        occupied_dates = db.session.query(
            func.date(Schedule.schedule_start_time).label('date')
        ).join(TrainingUser, TrainingUser.training_user_id == Schedule.training_user_id
               ).join(Trainer, Trainer.trainer_id == TrainingUser.trainer_id
                      ).join(TrainerAvailability, db.and_(
            Trainer.trainer_id == TrainerAvailability.trainer_id,
            func.weekday(Schedule.schedule_start_time) == TrainerAvailability.week_day
        )).filter(
            Trainer.trainer_id == trainer_id,
            func.year(Schedule.schedule_start_time) == year,
            func.month(Schedule.schedule_start_time) == month
        ).group_by(
            func.date(Schedule.schedule_start_time)
        ).having(
            func.max(TrainerAvailability.possible_lesson_cnt) <= func.count()
        ).all()

        for date, in occupied_dates:
            available_dates.discard(date.strftime('%Y-%m-%d'))

        # "근무 가능 날짜" 목록에서 조건을 충족하는 날짜를 제외한 결과 반환
        return sorted(list(available_dates))


@ns_trainer_schedule.route('/<int:trainer_id>/<int:year>/<int:month>/<int:day>')
class TrainerDaySchedule(Resource):
    def get(self, trainer_id, year, month, day):
        date_filter = date(year, month, day)

        trainer_details = db.session.query(
            Trainer.lesson_minutes,
            Trainer.lesson_change_range,
            TrainerAvailability.start_time,
            TrainerAvailability.end_time,
        ) \
            .join(TrainerAvailability, (TrainerAvailability.trainer_id == Trainer.trainer_id) \
                  & (TrainerAvailability.week_day == date_filter.weekday())) \
            .filter(Trainer.trainer_id == trainer_id,
                    Trainer.trainer_delete_flag == False) \
            .first()  # 가정: 모든 스케줄에 대해 lesson_minutes와 availability_start_time는 동일

        if trainer_details:
            formatted_start_time = trainer_details.start_time.strftime(
                "%H:%M") if trainer_details.start_time else None
            formatted_end_time = trainer_details.end_time.strftime(
                "%H:%M") if trainer_details.end_time else None

            result = {
                'lesson_minutes': trainer_details.lesson_minutes,
                'lesson_change_range': trainer_details.lesson_change_range,
                'availability_start_time': formatted_start_time,
                'availability_end_time': formatted_end_time
            }
        else:
            result = {}

        schedules = db.session.query(
            Schedule.schedule_id,
            Schedule.schedule_start_time
        ) \
            .join(TrainingUser, (TrainingUser.training_user_id == Schedule.training_user_id) \
                  & (TrainingUser.training_user_delete_flag == False) \
                  & (Schedule.schedule_delete_flag == False) \
                  & (db.func.date(Schedule.schedule_start_time) == date_filter)) \
            .join(Trainer, (Trainer.trainer_id == TrainingUser.trainer_id) \
                  & (Trainer.trainer_id == trainer_id) \
                  & (Trainer.trainer_delete_flag == False)) \
            .all()

        result['schedules'] = [{
            'schedule_id': schedule.schedule_id,
            'schedule_start_time': schedule.schedule_start_time
        } for schedule in schedules]

        return jsonify(result)

# todo: 스케쥴 조회시 스케쥴 상태 조건 추가