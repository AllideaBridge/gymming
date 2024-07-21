from datetime import datetime

from app.common.exceptions import BadRequestError
from app.entities.entity_trainer_user import TrainerUser
from app.entities.entity_users import Users
from app.repositories.repository_trainer import trainer_repository
from app.repositories.repository_trainer_user import trainer_user_repository
from app.repositories.repository_users import user_repository
from app.routes.models.model_trainer_user import UsersRelatedTrainerResponse, CreateTrainerUserRelationRequest, \
    TrainersRelatedUserResponse, UserDetailRelatedTrainerResponse, UpdateTrainerUserRequest
from app.services.service_image import ImageService


class TrainerUserService:
    def __init__(self):
        self.tu_repository = trainer_user_repository
        self.user_repository = user_repository
        self.trainer_repository = trainer_repository
        self.image_service = ImageService()

    def get_users_related_trainer(self, trainer_id: int, delete_flag: bool = False):
        trainer = self.trainer_repository.select_trainer_by_id(trainer_id)
        if not trainer:
            raise BadRequestError("트레이너가 존재하지 않습니다.")

        entities = self.tu_repository.select_with_users_by_trainer_id(trainer_id, delete_flag)

        results = []
        for trainer_user, user in entities:
            user_profile_img_url = self.image_service.get_presigned_url(f'user/{user.user_id}/profile')
            user.user_profile_img_url = user_profile_img_url
            results.append(UsersRelatedTrainerResponse.to_dict(trainer_user, user))
        return results

    def get_trainers_related_user(self, user_id):
        user = self.user_repository.select_by_id(user_id)
        if not user:
            raise BadRequestError("유저가 존재하지 않습니다.")

        entities = self.tu_repository.select_with_trainers_by_user_id(user_id)

        results = []
        for trainer_user, trainer in entities:
            trainer_profile_img_url = self.image_service.get_presigned_url(f'trainer/{trainer.trainer_id}/profile')
            trainer.trainer_profile_img_url = trainer_profile_img_url
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

        user_profile_img_url = self.image_service.get_presigned_url(f'user/{user.user_id}/profile')
        user.user_profile_img_url = user_profile_img_url

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

    def update_trainer_user(self, trainer_id, user_id, data: UpdateTrainerUserRequest):
        user = self.user_repository.select_by_id(user_id)
        if not user:
            raise BadRequestError(f"유저가 존재하지 않습니다. User_id: {user_id}")

        trainer = self.trainer_repository.select_trainer_by_id(trainer_id)
        if not trainer:
            raise BadRequestError(f"트레이너가 존재하지 않습니다. Trainer: {trainer_id}")

        trainer_user: TrainerUser = self.tu_repository.select_by_trainer_id_and_user_id(
            trainer_id=trainer_id, user_id=user_id)
        if not trainer_user:
            raise BadRequestError(f"해당 트레이너에게 트레이닝 받는 유저가 없습니다. Trainer_id: {trainer_id}, User_id: {user_id}")

        trainer_user.lesson_total_count = data.lesson_total_count
        trainer_user.lesson_current_count = data.lesson_current_count
        trainer_user.exercise_days = data.exercise_days
        trainer_user.special_notes = data.special_notice
        self.tu_repository.update_trainer_user()

    def delete_trainer_user(self, trainer_id, user_id):
        trainer_user: TrainerUser = self.tu_repository.select_by_trainer_id_and_user_id(
            trainer_id=trainer_id, user_id=user_id)
        if not trainer_user:
            raise BadRequestError(f"해당 트레이너에게 트레이닝 받는 유저가 없습니다. Trainer_id: {trainer_id}, User_id: {user_id}")

        if trainer_user.trainer_user_delete_flag or trainer_user.deleted_at:
            raise BadRequestError(f"이미 종료된 유저입니다. Trainer_id: {trainer_id}, User_id: {user_id}")

        trainer_user.trainer_user_delete_flag = True
        trainer_user.deleted_at = datetime.utcnow()
        self.tu_repository.update_trainer_user()


trainer_user_service = TrainerUserService()
