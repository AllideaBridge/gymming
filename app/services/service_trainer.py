from app.common.exceptions import BadRequestError
from app.repositories.repository_trainer import TrainerRepository
from app.repositories.repository_trainer_availability import TrainerAvailabilityRepository


class TrainerService:

    @staticmethod
    def get_trainer_by_social_id(trainer_social_id):
        return TrainerRepository.select_trainer_by_social_id(trainer_social_id)

    @staticmethod
    def create_trainer_only_social_id(trainer_social_id):

        from database import db
        return TrainerRepository(db=db).insert_trainer_with_social_id(trainer_social_id)

    def update_trainer(self, trainer_id, data):
        trainer = TrainerRepository.select_trainer_by_id(trainer_id)
        if trainer is None:
            raise BadRequestError(message="존재하지 않는 트레이너입니다.")

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

        TrainerRepository.update(trainer)
        trainer_availability = data.get('trainer_availability')

        if trainer_availability is not None:
            TrainerAvailabilityRepository.delete_availability_by_trainer(trainer_id)
            TrainerAvailabilityRepository.insert_availabilities(trainer_id, trainer_availability)

        return {"message": "success"}
