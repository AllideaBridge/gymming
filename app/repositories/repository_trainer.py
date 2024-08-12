from flask_sqlalchemy import SQLAlchemy

from app.repositories.repository_base import BaseRepository
from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_availability import TrainerAvailability


class TrainerRepository(BaseRepository[Trainer]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(Trainer, db)

    def select_trainer_details_by_id_and_date(self, trainer_id, date):
        return self.db.session.query(
            Trainer.lesson_minutes,
            TrainerAvailability.start_time,
            TrainerAvailability.end_time
        ).join(TrainerAvailability, TrainerAvailability.trainer_id == Trainer.trainer_id
               & (TrainerAvailability.week_day == date.weekday())
               ).filter(Trainer.trainer_id == trainer_id, Trainer.trainer_delete_flag == False).first()

    @staticmethod
    def select_trainer_by_id(trainer_id):
        return Trainer.query.filter_by(trainer_id=trainer_id).first()

    @staticmethod
    def select_trainer_by_social_id(trainer_social_id):
        return Trainer.query.filter_by(trainer_social_id=trainer_social_id).first()

    def insert_trainer_with_social_id(self, trainer_social_id):
        trainer = Trainer(
            trainer_social_id=trainer_social_id
        )
        self.db.session.add(trainer)
        self.db.session.commit()
        return trainer
