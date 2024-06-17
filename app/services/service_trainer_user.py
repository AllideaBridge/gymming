from app.common.exceptions import BadRequestError
from app.entities.entity_trainer_user import TrainerUser
from app.entities.entity_users import Users
from app.repositories.repository_trainer import trainer_repository
from app.repositories.repository_trainer_user import trainer_user_repository
from app.repositories.repository_users import user_repository
from app.routes.models.model_trainer_user import UsersRelatedTrainerResponse, CreateTrainerUserRelationRequest, \
    TrainersRelatedUserResponse, UserDetailRelatedTrainerResponse


class TrainerUserService:
    def __init__(self):
        self.tu_repository = trainer_user_repository
        self.user_repository = user_repository
        self.trainer_repository = trainer_repository

    def get_users_related_trainer(self, trainer_id: int, delete_flag: bool = False):
        trainer = self.trainer_repository.select_trainer_by_id(trainer_id)
        if not trainer:
            raise BadRequestError("트레이너가 존재하지 않습니다.")

        entities = self.tu_repository.select_with_users_by_trainer_id(trainer_id, delete_flag)

        results = []
        for trainer_user, user in entities:
            results.append(UsersRelatedTrainerResponse.to_dict(trainer_user, user))
        return results

    def get_trainers_related_user(self, user_id):
        user = self.user_repository.select_by_id(user_id)
        if not user:
            raise BadRequestError("유저가 존재하지 않습니다.")

        entities = self.tu_repository.select_with_trainers_by_user_id(user_id)

        results = []
        for trainer_user, trainer in entities:
            results.append(TrainersRelatedUserResponse.to_dict(trainer_user, trainer))
        return results

    def get_user_detail_related_trainer(self, trainer_id, user_id):
        user = self.user_repository.select_by_id(user_id)
        if not user:
            raise BadRequestError(f"유저가 존재하지 않습니다. User_id: {user_id}")

        trainer = self.trainer_repository.select_trainer_by_id(trainer_id)
        if not trainer:
            raise BadRequestError(f"트레이너가 존재하지 않습니다. Trainer: {trainer_id}")

        trainer_user = self.tu_repository.select_by_trainer_id_and_user_id(trainer_id=trainer_id, user_id=user_id)
        if not trainer_user:
            raise BadRequestError(f"해당 트레이너에게 트레이닝 받는 유저가 없습니다. Trainer_id: {trainer_id}, User_id: {user_id}")

        return UserDetailRelatedTrainerResponse.to_dict(user, trainer_user)

    def create_trainer_user_relation(self, trainer_id, data: CreateTrainerUserRelationRequest):
        user: Users = self.user_repository.select_by_username_and_phone_number(data.user_name, data.phone_number)
        if not user:
            raise BadRequestError("유저가 존재하지 않습니다.")

        trainer_user = self.tu_repository.select_by_trainer_id_and_user_id(trainer_id, user.user_id)
        if trainer_user:
            raise BadRequestError("이미 해당 트레이너와 매핑된 유저입니다.")

        new_trainer_user = TrainerUser(
            trainer_id=trainer_id,
            user_id=user.user_id,
            lesson_total_count=data.lesson_total_count,
            lesson_current_count=data.lesson_current_count,
            exercise_days=data.exercise_days,
            special_notes=data.special_notice
        )

        self.tu_repository.create_trainer_user(new_trainer_user)


trainer_user_service = TrainerUserService()
