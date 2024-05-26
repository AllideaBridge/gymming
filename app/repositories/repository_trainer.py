from database import db
from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_availability import TrainerAvailability


class TrainerRepository:
    def select_trainer_details_by_id_and_date(self, trainer_id, date):
        return db.session.query(
            Trainer.lesson_minutes,
            TrainerAvailability.start_time,
            TrainerAvailability.end_time
        ).join(TrainerAvailability, TrainerAvailability.trainer_id == Trainer.trainer_id
               & (TrainerAvailability.week_day == date.weekday())
               ).filter(Trainer.trainer_id == trainer_id, Trainer.trainer_delete_flag == False).first()

    def select_trainer_by_id(self, trainer_id):
        return Trainer.query.filter_by(trainer_id=trainer_id).first()