from pydantic import BaseModel, Field, field_validator

from app.common.constants import SCHEDULE_MODIFIED
from app.common.exceptions import BadRequestError
from app.utils.util_time import validate_datetime


class ScheduleCreateRequest(BaseModel):
    trainer_id: int = Field(description='trainer id')
    user_id: int = Field(description='user id')
    schedule_start_time: str = Field(description='schedule_start_time')

    @field_validator('schedule_start_time')
    @classmethod
    def validate_schedule_start_time(cls, v):
        return validate_datetime(v)


class ScheduleSetRequest(BaseModel):
    start_time: str = Field(description='schedule start time')
    status: str = Field(description='schedule status')

    @field_validator('start_time')
    @classmethod
    def validate_schedule_start_time(cls, v):
        return validate_datetime(v)

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in [SCHEDULE_MODIFIED]:
            raise BadRequestError(message='schedule status must be MODIFIED')