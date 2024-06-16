from app.repositories.repository_trainer import TrainerRepository


class TrainerService:
    @staticmethod
    def get_trainer_by_social_id(trainer_social_id):
        return TrainerRepository.select_trainer_by_social_id(trainer_social_id)

    @staticmethod
    def create_trainer_only_social_id(trainer_social_id):
        return TrainerRepository.insert_trainer_with_social_id(trainer_social_id)
