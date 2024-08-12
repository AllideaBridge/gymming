from typing import Any
from typing_extensions import Self

from pydantic import BaseModel, Field, field_validator


class FcmAuthRequest(BaseModel):
    fcm_token: str = Field(description='fcm token')

    @field_validator('fcm_token')
    @classmethod
    def validate(cls, v):
        # 필드 검사 로직
        return v
