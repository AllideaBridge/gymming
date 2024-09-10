import datetime
from typing import Any, List
from typing_extensions import Self

from pydantic import BaseModel, Field, field_validator


class FcmAuthRequest(BaseModel):
    fcm_token: str = Field(description='fcm token')

    @field_validator('fcm_token')
    @classmethod
    def validate(cls, v):
        # 필드 검사 로직
        return v


class KakaoAuthRequest(BaseModel):
    kakao_token: str = Field(description='kakao token')


class KakaoUserRegisterRequest(KakaoAuthRequest):
    user_name: str = Field(description='user name')
    user_phone_number: str = Field(description='user phone number')
    user_birthday: str = Field(description='user birthday')
    user_gender: str = Field(description='user gender')


class TrainerAvailabilityRequest(BaseModel):
    week_day: int = Field(description='근무 요일'),  # 0: mon, 1: tue, ..., 6: sun
    start_time: str = Field(description='근무 시작 시간'),
    end_time: str = Field(description='근무 종료 시간')


class KakaoTrainerRegisterRequest(KakaoAuthRequest):
    trainer_name: str = Field(description='trainer name'),
    trainer_phone_number: str = Field(description='trainer phone number'),
    trainer_gender: str = Field(description='trainer gender'),
    trainer_birthday: str = Field(description='trainer birthday'),
    description: str = Field(description='trainer description'),
    lesson_name: str = Field(description='lesson name'),
    lesson_price: int = Field(description='lesson price'),
    lesson_change_range: int = Field(description='lesson change range'),
    center_name: str = Field(description='center name'),
    center_location: str = Field(description='center location'),
    center_number: str = Field(description='center name'),
    center_type: str = Field(description='center type'),
    trainer_availability: List[TrainerAvailabilityRequest] = Field(description='트레이너 근무 요일 및 시간')
