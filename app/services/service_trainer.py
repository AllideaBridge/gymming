from app.common.exceptions import BadRequestError
from app.entities.entity_trainer_fcm_token import TrainerFcmToken


class TrainerService:
    def __init__(self, trainer_repository, trainer_availability_repository, trainer_fcm_repository):
        self.trainer_repository = trainer_repository
        self.trainer_availability_repository = trainer_availability_repository
        self.trainer_fcm_repository = trainer_fcm_repository

    def get_trainer_by_social_id(self, trainer_social_id):
        return self.trainer_repository.select_trainer_by_social_id(trainer_social_id)

    def create_trainer_only_social_id(self, trainer_social_id):
        return self.trainer_repository.insert_trainer_with_social_id(trainer_social_id)

    def update_trainer(self, trainer_id, data):
        trainer = self.trainer_repository.get(trainer_id)
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

        self.trainer_repository.update(trainer)
        trainer_availability = data.get('trainer_availability')

        if trainer_availability is not None:
            self.trainer_availability_repository.delete_availability_by_trainer(trainer_id)
            self.trainer_availability_repository.insert_availabilities(trainer_id, trainer_availability)

        return {"message": "success"}

    def create_trainer_fcm_token(self, trainer_id, body):
        old_token = self.trainer_fcm_repository.get_by_trainer_id(trainer_id=trainer_id)
        if old_token is not None:
            self.trainer_fcm_repository.delete(old_token)

        trainer_fcm_token = TrainerFcmToken(
            trainer_id=trainer_id,
            fcm_token=body.fcm_token
        )

        self.trainer_fcm_repository.create(trainer_fcm_token)
