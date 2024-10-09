from typing import List

from flask_restx import fields, Model
from pydantic import BaseModel, Field, field_validator

from app.common.constants import const
from app.common.exceptions import BadRequestError

user_of_trainer = Model('UserOfTrainer', {
    'user_id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'user_name': fields.String(description='User name'),
    'user_profile_img_url': fields.String(description='User profile image URL'),
    'exercise_days': fields.String(description='Exercise Days'),
    'lesson_current_count': fields.Integer(description='Lesson Current Count'),
    'lesson_total_count': fields.Integer(description='Lesson Total Count'),
    'registered_date': fields.String(description='등록 날짜'),
    'last_date': fields.String(description='종료 날짜')
})

users_of_trainer = {
    'results': fields.List(fields.Nested(user_of_trainer))
}


class UserTrainer(BaseModel):
    trainer_id: int = Field(description="trainer_id")
    trainer_name: str = Field(description="trainer_name")
    trainer_profile_img_url: str = Field(description="trainer_profile_img_url")
    lesson_name: str = Field(description="lesson_name")
    lesson_current_count: int = Field(description="lesson_current_count")
    lesson_total_count: int = Field(description="lesson_total_count")
    center_name: str = Field(description="center_name")
    center_location: str = Field(description="center_location")


class CreateTrainerUserRelationRequest(BaseModel):
    user_name: str = Field()
    phone_number: str = Field()
    lesson_total_count: int = Field()
    lesson_current_count: int = Field()
    exercise_days: str | None = Field(default=None)
    special_notice: str | None = Field(default=None)

    # @field_validator('user_name')
    # @classmethod
    # def validate(cls, value: str):
    #     return value

    # @field_validator('phone_number')
    # @classmethod
    # def validate(cls, value: str):
    #     return value

    # @field_validator('lesson_total_count')
    # @classmethod
    # def validate_lesson_total_count(cls, value: int):
    #     if value < 0:
    #         raise BadRequestError()
    #     return value

    # @field_validator('lesson_current_count')
    # @classmethod
    # def validate_lesson_current_count(cls, value, values):
    #     if value < 0:
    #         raise BadRequestError("Current lesson count cannot be negative.")
    #     total_count = values.get('lesson_total_count')
    #     if total_count is not None and value > total_count:
    #         raise BadRequestError("Current lesson count cannot exceed total lesson count.")
    #     return value

    # @field_validator('exercise_days')
    # @classmethod
    # def validate_exercise_days(cls, value: str):
    #     return value
    #
    # @field_validator('special_notice')
    # @classmethod
    # def validate_special_notice(cls, value: str):
    #     return value


class UpdateTrainerUserRequest(BaseModel):
    lesson_total_count: int | None = Field()
    lesson_current_count: int | None = Field()
    exercise_days: str | None = Field()
    special_notice: str | None = Field()

    @field_validator('lesson_total_count')
    @classmethod
    def validate(cls, value: int | None):
        if value is not None and value < 0:
            raise BadRequestError()
        return value

    @field_validator('lesson_current_count')
    @classmethod
    def validate(cls, value: int | None):
        if value is not None and value < 0:
            raise BadRequestError()
        return value

    @field_validator('exercise_days')
    @classmethod
    def validate(cls, value: str | None):
        return value

    @field_validator('special_notice')
    @classmethod
    def validate(cls, value: str | None):
        return value


class UserTrainersResponse(BaseModel):
    results: List[UserTrainer]


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
    def to_dict(trainer_user, user):
        return {
            "user_id": trainer_user.user_id,
            "user_name": user.user_name,
            "user_profile_img_url": user.user_profile_img_url,
            "exercise_days": trainer_user.exercise_days,
            "lesson_current_count": trainer_user.lesson_current_count,
            "lesson_total_count": trainer_user.lesson_total_count,
            "registered_date": trainer_user.created_at.strftime(const.DATETIMEFORMAT),
            "last_date": trainer_user.deleted_at.strftime(
                const.DATETIMEFORMAT) if trainer_user.deleted_at is not None else None
        }


class TrainersRelatedUserResponse:
    trainer_id: int
    trainer_name: str
    trainer_profile_img_url: str
    lesson_name: str
    lesson_total_count: int
    lesson_current_count: int
    center_name: str
    center_location: str

    @staticmethod
    def to_dict(trainer_user, trainer):
        return {
            "trainer_id": trainer.trainer_id,
            "trainer_name": trainer.trainer_name,
            "trainer_profile_img_url": trainer.trainer_profile_img_url,
            "lesson_name": trainer.lesson_name,
            "lesson_total_count": trainer_user.lesson_total_count,
            "lesson_current_count": trainer_user.lesson_current_count,
            "center_name": "Center 아직 적용 안함",
            "center_location": "Center 아직 적용 안함"
        }


class UserDetailRelatedTrainerResponse:
    name: str
    email: str
    gender: str
    phone_number: str
    user_profile_img_url: str
    delete_flag: bool
    birthday: str
    lesson_total_count: int
    lesson_current_count: int
    exercise_days: str
    special_notice: str
    registered_date: str
    last_date: str

    @staticmethod
    def to_dict(user, trainer_user):
        return {
            "name": user.user_name,
            "email": user.user_email,
            "gender": user.user_gender,
            "phone_number": user.user_phone_number,
            "user_profile_img_url": user.user_profile_img_url,
            "delete_flag": user.user_delete_flag,
            "birthday": user.user_birthday,
            "lesson_total_count": trainer_user.lesson_total_count,
            "lesson_current_count": trainer_user.lesson_current_count,
            "exercise_days": trainer_user.exercise_days,
            "special_notice": trainer_user.special_notes,
            "registered_date": trainer_user.created_at.strftime(const.DATETIMEFORMAT),
            "last_date": trainer_user.deleted_at.strftime(
                const.DATETIMEFORMAT) if trainer_user.deleted_at is not None else None
        }


user_detail_of_trainer = Model('User Details of Trainer', {
    'name': fields.String(description='User name'),
    'email': fields.String(description='User email'),
    'gender': fields.String(description='User gender'),
    'phone_number': fields.String(description='User phone number'),
    'user_profile_img_url': fields.String(description='User profile url'),
    'delete_flag': fields.Boolean(),
    'birthday': fields.String(description='User birthday'),
    'lesson_total_count': fields.Integer(description='Lesson Total Count'),
    'lesson_current_count': fields.Integer(description='Lesson Current Count'),
    'exercise_days': fields.String(description='User exercise days'),
    'special_notice': fields.String(description='User special notice'),
    'registered_date': fields.String(description='등록 날짜'),
    'last_date': fields.String(description='종료 날짜'),
})
