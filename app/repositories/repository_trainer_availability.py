from datetime import datetime

from app.common.constants import TIMEFORMAT
from app.entities.entity_trainer_availability import TrainerAvailability
from app.entities.entity_trainer import Trainer
from app.utils.util_time import calculate_lesson_slots
from database import db


class TrainerAvailabilityRepository:
    def select_week_day_by_trainer_id(self, trainer_id):
        available_week_days = db.session.query(
            TrainerAvailability.week_day
        ).filter_by(
            trainer_id=trainer_id
        ).all()

        return available_week_days

    @staticmethod
    def delete_availability_by_trainer(trainer_id):
        availabilities = TrainerAvailability.query.filter_by(trainer_id=trainer_id).all()
        for availability in availabilities:
            db.session.delete(availability)

        db.session.commit()

    @staticmethod
    def insert_availabilities(trainer_id, availabilities):
        trainer = Trainer.query.filter_by(trainer_id=trainer_id).first()
        lesson_minutes = trainer.lesson_minutes
        for availability in availabilities:
            start_time = datetime.strptime(availability.get('start_time'), TIMEFORMAT).time()
            end_time = datetime.strptime(availability.get('end_time'), TIMEFORMAT).time()
            possible_lesson_cnt = calculate_lesson_slots(start_time, end_time, lesson_minutes)

            trainer_availability = TrainerAvailability(
                trainer_id=trainer_id,
                week_day=availability.get('week_day'),
                start_time=availability.get('start_time'),
                end_time=availability.get('end_time'),
                possible_lesson_cnt=possible_lesson_cnt
            )
            db.session.add(trainer_availability)

        db.session.commit()
