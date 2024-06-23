from database import db
from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_availability import TrainerAvailability


class TrainerRepository:
    @staticmethod
    def select_trainer_details_by_id_and_date(trainer_id, date):
        return db.session.query(
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

    @staticmethod
    def insert_trainer_with_social_id(trainer_social_id):
        trainer = Trainer(
            trainer_social_id=trainer_social_id
        )
        db.session.add(trainer)
        db.session.commit()
        return trainer

    @staticmethod
    def update(trainer, data):
        trainer.trainer_name = data.get('trainer_name', trainer.trainer_name)
        trainer.trainer_phone_number = data.get('trainer_phone_number', trainer.trainer_phone_number)
        trainer.trainer_gender = data.get('trainer_gender', trainer.trainer_gender)
        trainer.trainer_birthday = data.get('trainer_birthday', trainer.trainer_birthday)
        trainer.description = data.get('description', trainer.description)
        trainer.lesson_name = data.get('lesson_name', trainer.lesson_name)
        trainer.lesson_price = data.get('lesson_price', trainer.lesson_price)
        trainer.lesson_minutes = data.get('lesson_minutes', trainer.lesson_minutes)
        trainer.lesson_change_range = data.get('lesson_change_range', trainer.lesson_change_range)
        trainer.center_name = data.get('center_name', trainer.center_name)
        trainer.center_location = data.get('center_location', trainer.center_location)
        trainer.center_number = data.get('center_number', trainer.center_number)
        trainer.center_type = data.get('center_type', trainer.center_type)

        db.session.commit()
        return trainer


trainer_repository = TrainerRepository()
