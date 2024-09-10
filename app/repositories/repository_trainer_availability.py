from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from app.common.constants import TIMEFORMAT
from app.entities.entity_trainer_availability import TrainerAvailability
from app.entities.entity_trainer import Trainer
from app.repositories.repository_base import BaseRepository
from app.utils.util_time import calculate_lesson_slots


class TrainerAvailabilityRepository(BaseRepository[TrainerAvailability]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(TrainerAvailability, db)

    def get_by_trainer_id(self, trainer_id):
        return TrainerAvailability.query.filter_by(trainer_id=trainer_id).all()

    def select_week_day_by_trainer_id(self, trainer_id):
        available_week_days = self.db.session.query(
            TrainerAvailability.week_day
        ).filter_by(
            trainer_id=trainer_id
        ).all()

        return available_week_days

    def delete_availability_by_trainer(self, trainer_id):
        availabilities = TrainerAvailability.query.filter_by(trainer_id=trainer_id).all()
        for availability in availabilities:
            self.db.session.delete(availability)

        self.db.session.commit()

    def insert_availabilities(self, trainer_id, availabilities):
        trainer = Trainer.query.filter_by(trainer_id=trainer_id).first()
        lesson_minutes = trainer.lesson_minutes
        for availability in availabilities:
            start_time = datetime.strptime(availability.start_time, TIMEFORMAT).time()
            end_time = datetime.strptime(availability.end_time, TIMEFORMAT).time()
            possible_lesson_cnt = calculate_lesson_slots(start_time, end_time, lesson_minutes)

            trainer_availability = TrainerAvailability(
                trainer_id=trainer_id,
                week_day=availability.week_day,
                start_time=start_time,
                end_time=end_time,
                possible_lesson_cnt=possible_lesson_cnt
            )
            self.db.session.add(trainer_availability)

        self.db.session.commit()
