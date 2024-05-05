from datetime import datetime

from sqlalchemy import func, and_, literal_column
from sqlalchemy.sql.functions import coalesce

from app.common.constants import SCHEDULE_SCHEDULED
from app.entities.entity_trainer_availability import TrainerAvailability
from app.entities.entity_trainer import Trainer
from app.entities.entity_center import Center
from app.entities.entity_training_user import TrainingUser
from app.entities.entity_schedule import Schedule
from database import db


class ScheduleRepository:
    def select_schedule_day_by_tu_id_and_year_month(self, training_user_id, year, month, page=1, per_page=10):
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        schedules = Schedule.query.filter(
            Schedule.training_user_id == training_user_id,
            Schedule.schedule_start_time >= start_date,
            Schedule.schedule_start_time < end_date
        ).paginate(page=page, per_page=per_page)

        return schedules

    def select_month_schedule_time_by_user_id(self, user_id, year, month):
        schedules = db.session.query(func.distinct(func.date(Schedule.schedule_start_time))).join(TrainingUser).filter(
            TrainingUser.user_id == user_id,
            db.extract('year', Schedule.schedule_start_time) == year,
            db.extract('month', Schedule.schedule_start_time) == month).all()
        return schedules

    def select_day_schedule_by_user_id(self, user_id, year, month, day):
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

    def select_by_id(self, schedule_id):
        schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        return schedule

    def select_conflict_schedule_by_trainer_id_and_request_time(self, trainer_id, request_time):
        conflict_schedule = db.session.query(Schedule). \
            join(TrainingUser, and_(TrainingUser.training_user_id == Schedule.training_user_id,
                                    Schedule.schedule_status == SCHEDULE_SCHEDULED)). \
            join(Trainer, and_(Trainer.trainer_id == TrainingUser.trainer_id,
                               Trainer.trainer_id == trainer_id)). \
            filter(func.abs(func.timestampdiff(literal_column('MINUTE'), Schedule.schedule_start_time,
                                               request_time)) < Trainer.lesson_minutes). \
            first()

        return conflict_schedule

    def select_full_date_by_trainer_id_and_year_month(self, trainer_id, year, month):
        full_dates = db.session.query(
            func.date(Schedule.schedule_start_time).label('date')
        ).join(TrainingUser, TrainingUser.training_user_id == Schedule.training_user_id
               ).join(Trainer, Trainer.trainer_id == TrainingUser.trainer_id
                      ).join(TrainerAvailability, and_(
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

        return full_dates

    def select_conflict_trainer_schedule_by_time(self, trainer_id, start_time):
        schedule = db.session.query(Schedule). \
            join(TrainingUser, and_(TrainingUser.training_user_id == Schedule.training_user_id,
                                    Schedule.schedule_status == SCHEDULE_SCHEDULED)). \
            join(Trainer, and_(Trainer.trainer_id == TrainingUser.trainer_id,
                               Trainer.trainer_id == trainer_id)). \
            filter(func.abs(func.timestampdiff(literal_column('MINUTE'), Schedule.schedule_start_time,
                                               start_time)) < Trainer.lesson_minutes). \
            first()

        return schedule

    def select_schedule_by_id(self, schedule_id):
        schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        return schedule

    def insert_schedule(self, schedule):
        db.session.add(schedule)
        db.session.commit()

    def delete_schedule(self, schedule_id):
        schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        if schedule:
            schedule.schedule_delete_flag = True
            db.session.commit()
            return True
        return False


'''
    Repository Naming Rule
        method(select, update, delete, insert)_Record_by_condition
'''

'''
    Service Naming Rule
        
'''
