from datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_, literal_column
from sqlalchemy.sql.functions import coalesce

from app.common.constants import SCHEDULE_SCHEDULED
from app.entities.entity_trainer_availability import TrainerAvailability
from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_user import TrainerUser
from app.entities.entity_schedule import Schedule
from app.entities.entity_users import Users
from app.repositories.repository_base import BaseRepository


class ScheduleRepository(BaseRepository[Schedule]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(Schedule, db)

    def select_schedule_day_by_tu_id_and_year_month(self, trainer_user_id, year, month, page=1, per_page=10):
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        schedules = Schedule.query.filter(
            Schedule.trainer_user_id == trainer_user_id,
            Schedule.schedule_start_time >= start_date,
            Schedule.schedule_start_time < end_date
        ).paginate(page=page, per_page=per_page)

        return schedules

    def select_month_schedule_time_by_user_id(self, user_id, year, month):
        schedules = (
            self.db.session.query(func.distinct(func.date(Schedule.schedule_start_time))).join(TrainerUser).filter(
                TrainerUser.user_id == user_id,
                self.db.extract('year', Schedule.schedule_start_time) == year,
                self.db.extract('month', Schedule.schedule_start_time) == month)
            .order_by(func.date(Schedule.schedule_start_time).asc())
            .all())
        return schedules

    def select_day_schedule_by_user_id(self, user_id, year, month, day):
        schedules = (self.db.session.query(
            Schedule.schedule_id,
            Trainer.trainer_id,
            Schedule.schedule_start_time,
            Trainer.trainer_name,
            coalesce(Trainer.lesson_name, '').label('lesson_name'),
            coalesce(Trainer.center_name, '').label('center_name'),
            coalesce(Trainer.center_location, '').label('center_location'),
            Trainer.lesson_change_range,
            Trainer.lesson_minutes
        )
                     .join(TrainerUser, TrainerUser.trainer_user_id == Schedule.trainer_user_id)
                     .join(Trainer, TrainerUser.trainer_id == Trainer.trainer_id)
                     .filter(TrainerUser.user_id == user_id,
                             func.year(Schedule.schedule_start_time) == year,
                             func.month(Schedule.schedule_start_time) == month,
                             func.day(Schedule.schedule_start_time) == day)
                     .all())

        return schedules

    def select_conflict_schedule_by_trainer_id_and_request_time(self, trainer_id, request_time):
        conflict_schedule = self.db.session.query(Schedule). \
            join(TrainerUser, and_(TrainerUser.trainer_user_id == Schedule.trainer_user_id,
                                   Schedule.schedule_status == SCHEDULE_SCHEDULED)). \
            join(Trainer, and_(Trainer.trainer_id == TrainerUser.trainer_id,
                               Trainer.trainer_id == trainer_id)). \
            filter(func.abs(func.timestampdiff(literal_column('MINUTE'), Schedule.schedule_start_time,
                                               request_time)) < Trainer.lesson_minutes). \
            first()

        return conflict_schedule

    def select_full_date_by_trainer_id_and_year_month(self, trainer_id, year, month):
        full_dates = self.db.session.query(
            func.date(Schedule.schedule_start_time).label('date')
        ).join(TrainerUser, TrainerUser.trainer_user_id == Schedule.trainer_user_id
               ).join(Trainer, Trainer.trainer_id == TrainerUser.trainer_id
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
        schedule = self.db.session.query(Schedule). \
            join(TrainerUser, and_(TrainerUser.trainer_user_id == Schedule.trainer_user_id,
                                   Schedule.schedule_status == SCHEDULE_SCHEDULED)). \
            join(Trainer, and_(Trainer.trainer_id == TrainerUser.trainer_id,
                               Trainer.trainer_id == trainer_id)). \
            filter(func.abs(func.timestampdiff(literal_column('MINUTE'), Schedule.schedule_start_time,
                                               start_time)) < Trainer.lesson_minutes). \
            first()

        return schedule

    def select_day_schedule_by_trainer_id(self, trainer_id, date):
        return self.db.session.query(
            Schedule.schedule_start_time
        ).join(TrainerUser, (TrainerUser.trainer_user_id == Schedule.trainer_user_id)
               & (TrainerUser.trainer_id == trainer_id)
               & (TrainerUser.trainer_user_delete_flag == False)
               & (Schedule.schedule_delete_flag == False)
               & (self.db.func.date(Schedule.schedule_start_time) == date)
               ).all()

    def select_week_schedule_by_trainer_id(self, trainer_id, start_date, end_date):
        return self.db.session.query(Users.user_id, Users.user_name, Schedule.schedule_start_time) \
            .join(TrainerUser,
                  (TrainerUser.trainer_user_id == Schedule.trainer_user_id) \
                  & (TrainerUser.trainer_id == trainer_id) \
                  & (self.db.func.date(Schedule.schedule_start_time) >= start_date) \
                  & (self.db.func.date(Schedule.schedule_start_time) <= end_date)) \
            .join(Users, Users.user_id == TrainerUser.user_id) \
            .all()

    def select_month_schedule_by_user_id_and_trainer_id(self, trainer_id, user_id, start_date, end_date):
        return self.db.session.query(
            Schedule.schedule_id,
            Schedule.schedule_start_time
        ).join(TrainerUser, (TrainerUser.trainer_id == trainer_id)
               & (TrainerUser.user_id == user_id)
               & (self.db.func.date(Schedule.schedule_start_time) >= start_date)
               & (self.db.func.date(Schedule.schedule_start_time) < end_date)
               & (TrainerUser.trainer_user_delete_flag == False)
               & (Schedule.schedule_delete_flag == False)
               ).all()

    def select_schedule_by_schedule_id(self, schedule_id):
        result = self.db.session.query(
            Schedule.schedule_id,
            Schedule.schedule_start_time,
            coalesce(Trainer.lesson_name, '').label('lesson_name'),
            Trainer.trainer_name,
            coalesce(Trainer.center_name, '').label('center_name'),
            coalesce(Trainer.center_location, '').label('center_location'),
        ).join(
            TrainerUser, Schedule.trainer_user_id == TrainerUser.trainer_user_id
        ).join(
            Trainer, TrainerUser.trainer_id == Trainer.trainer_id
        ).filter(
            Schedule.schedule_id == schedule_id,
            Schedule.schedule_delete_flag == False,
            TrainerUser.trainer_user_delete_flag == False,
            Trainer.trainer_delete_flag == False
        ).first()

        return result

    def select_lesson_change_range_by_schedue_id(self, schedule_id):
        result = self.db.session.query(
            coalesce(Trainer.lesson_change_range, 0).label('lesson_change_range')
        ).join(
            TrainerUser, Trainer.trainer_id == TrainerUser.trainer_id
        ).join(
            Schedule, TrainerUser.trainer_user_id == Schedule.trainer_user_id
        ).filter(
            and_(
                Schedule.schedule_id == schedule_id,
                Schedule.schedule_delete_flag == False,
                TrainerUser.trainer_user_delete_flag == False,
                Trainer.trainer_delete_flag == False
            )
        ).first()

        return result


# todo: 스케쥴 조회시 스케쥴 상태 조건 추가
'''
    Repository Naming Rule
        method(select, update, delete, insert)_Record_by_condition
'''

'''
    Service Naming Rule
        
'''
