from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_availability import TrainerAvailability
from app.common.exceptions import BadRequestError
from app.entities.entity_trainer_fcm_token import TrainerFcmToken


class TrainerService:
    def __init__(self, trainer_repository, trainer_availability_repository, trainer_fcm_repository, image_service):
        self.trainer_repository = trainer_repository
        self.trainer_availability_repository = trainer_availability_repository
        self.trainer_fcm_repository = trainer_fcm_repository
        self.image_service = image_service

    def get_trainer_by_id(self, trainer_id):
        trainer: Trainer = self.trainer_repository.get(trainer_id)
        trainer = trainer.__dict__

        trainer_availability = self.trainer_availability_repository.get_by_trainer_id(trainer_id)
        trainer['trainer_availability'] = trainer_availability

        presigned_url = self.image_service.get_presigned_url(f'trainer/{trainer_id}/profile')
        trainer['trainer_profile_img_url'] = presigned_url

        return trainer

    def get_trainer_by_social_id(self, trainer_social_id):
        return self.trainer_repository.select_trainer_by_social_id(trainer_social_id)

    def create_trainer_only_social_id(self, trainer_social_id):
        return self.trainer_repository.insert_trainer_with_social_id(trainer_social_id)

    def create_trainer(self, data):
        trainer = Trainer(
            trainer_social_id=data['trainer_social_id'],
            trainer_name=data.get('trainer_name'),
            trainer_phone_number=data.get('trainer_phone_number'),
            trainer_gender=data.get('trainer_gender'),
            trainer_birthday=data.get('trainer_birthday'),
            description=data.get('description'),
            lesson_name=data.get('lesson_name'),
            lesson_price=data.get('lesson_price'),
            lesson_minutes=60,
            lesson_change_range=data.get('lesson_change_range'),
            center_name=data.get('center_name'),
            center_location=data.get('center_location'),
            center_number=data.get('center_number'),
            center_type=data.get('center_type'),
        )

        trainer = self.trainer_repository.create(trainer)
        trainer_availabilities = data.get('trainer_availability', [])
        self.trainer_availability_repository.insert_availabilities(trainer.trainer_id, trainer_availabilities)

        return trainer

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
