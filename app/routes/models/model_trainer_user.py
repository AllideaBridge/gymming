from app.entities.entity_trainer import Trainer
from app.common.constants import DATETIMEFORMAT
from app.entities.entity_trainer_user import TrainerUser
from app.entities.entity_users import Users


class CreateTrainerUserRelationRequest:
    user_name: str
    phone_number: str
    lesson_total_count: int
    lesson_current_count: int
    exercise_days: str
    special_notice: str

    def __init__(self, data):
        self.user_name = data['user_name']
        self.phone_number = data['phone_number']
        self.lesson_total_count = data['lesson_total_count']
        self.lesson_current_count = data['lesson_current_count']
        self.exercise_days = data['exercise_days']
        self.special_notice = data['special_notice']


class UsersRelatedTrainerResponse:
    user_id: int
    user_name: str
    user_profile_img_url: str
    exercise_days: str
    lesson_current_count: int
    lesson_total_count: int
    registered_date: str
    last_date: str

    @staticmethod
    def to_dict(trainer_user: TrainerUser, user: Users):
        return {
            "user_id": trainer_user.user_id,
            "user_name": user.user_name,
            "user_profile_img_url": user.user_profile_img_url,
            "exercise_days": trainer_user.exercise_days,
            "lesson_current_count": trainer_user.lesson_current_count,
            "lesson_total_count": trainer_user.lesson_total_count,
            "registered_date": trainer_user.created_at.strftime(DATETIMEFORMAT),
            "last_date": trainer_user.deleted_at.strftime(
                DATETIMEFORMAT) if trainer_user.deleted_at is not None else None
        }


class TrainersRelatedUserResponse:
    trainer_id: int
    trainer_name: str
    trainer_pr_image_url: str
    lesson_total_count: int
    lesson_current_count: int
    center_name: str
    center_location: str

    @staticmethod
    def to_dict(trainer_user: TrainerUser, trainer: Trainer):
        return {
            "trainer_id": trainer.trainer_id,
            "trainer_name": trainer.trainer_name,
            "trainer_pr_image_url": trainer.trainer_pr_url,
            "lesson_total_count": trainer_user.lesson_total_count,
            "lesson_current_count": trainer_user.lesson_current_count,
            "center_name": "Center 아직 적용 안함",
            "center_location": "Center 아직 적용 안함"
        }
