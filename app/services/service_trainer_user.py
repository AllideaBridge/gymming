from app.repositories.repository_trainer_user import trainer_user_repository
from app.routes.models.model_trainer_user import TrainerUserResponse


class TrainerUserService:
    def __init__(self):
        self.tu_repository = trainer_user_repository

    def get_users_related_trainer(self, trainer_id: int, delete_flag: bool = False):
        entities = self.tu_repository.select_with_users_by_trainer_id(trainer_id, delete_flag)

        results = []
        for trainer_user, user in entities:
            results.append(TrainerUserResponse.to_dict(trainer_user, user))
        return results


trainer_user_service = TrainerUserService()
