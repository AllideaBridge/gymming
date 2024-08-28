# todo.txt : 스케쥴 생성 시간이 현재 시간보다 이후인지 체크
from datetime import datetime
from typing import Any
from typing_extensions import Self

from pydantic import BaseModel, Field, field_validator

from app.common.constants import DATETIMEFORMAT
from app.common.exceptions import BadRequestError


class ScheduleCreateRequest(BaseModel):
    trainer_id: int = Field(description='trainer id')
    user_id: int = Field(description='user id')
    schedule_start_time: str = Field(description='schedule_start_time')

    @field_validator('schedule_start_time')
    @classmethod
    def validate(cls, v):
        date_time = datetime.strptime(v, DATETIMEFORMAT)
        if date_time < datetime.now():
            raise BadRequestError('schedule_start_time must be in the future.')
        return v
