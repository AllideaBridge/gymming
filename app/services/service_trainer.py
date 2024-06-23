from app.common.exceptions import BadRequestError
from app.repositories.repository_trainer import TrainerRepository
from app.repositories.repository_trainer_availability import TrainerAvailabilityRepository


class TrainerService:
    @staticmethod
    def get_trainer_by_social_id(trainer_social_id):
        return TrainerRepository.select_trainer_by_social_id(trainer_social_id)

    @staticmethod
    def create_trainer_only_social_id(trainer_social_id):
        return TrainerRepository.insert_trainer_with_social_id(trainer_social_id)

    @staticmethod
    def update_trainer(trainer_id, data):
        trainer = TrainerRepository.select_trainer_by_id(trainer_id)
        if trainer is None:
            raise BadRequestError(message="존재하지 않는 트레이너입니다.")

        TrainerRepository.update(trainer, data)
        trainer_availability = data.get('trainer_availability')

        if trainer_availability is not None:
            TrainerAvailabilityRepository.delete_availability_by_trainer(trainer_id)
            TrainerAvailabilityRepository.insert_availabilities(trainer_id, trainer_availability)

        return {"message": "success"}
