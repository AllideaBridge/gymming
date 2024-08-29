from typing import Any

from flask_restx import fields, Model
from pydantic import BaseModel, Field, field_validator

from app.common.constants import const
from app.common.exceptions import BadRequestError


class CreateChangeTicketRequest(BaseModel):
    schedule_id: int = Field()
    change_from: str = Field()
    change_type: str = Field()
    change_reason: str = Field()
    start_time: str | None = Field(default=None)
    as_is_date: str = Field()

    @field_validator('shcedule_id')
    @classmethod
    def validate(cls, value: int):
        if value < 0:
            raise BadRequestError()
        return value

    @field_validator('change_from')
    @classmethod
    def validate(cls, value: str):
        if value not in [const.CHANGE_FROM_USER, const.CHANGE_FROM_TRAINER]:
            raise BadRequestError()
        return value

    @field_validator('change_type')
    @classmethod
    def validate(cls, value: str):
        if value not in [const.CHANGE_TICKET_TYPE_MODIFY, const.CHANGE_TICKET_TYPE_CANCEL]:
            raise BadRequestError()
        return value

    @field_validator('change_reason')
    @classmethod
    def validate(cls, value: str):
        return value

    @field_validator('start_time')
    @classmethod
    def validate(cls, value: str):
        return value


class UpdateChangeTicketRequest(BaseModel):
    change_from: str = Field()
    change_type: str = Field()
    status: str = Field()
    change_reason: str = Field()
    reject_reason: str = Field()
    start_time: str = Field()

    @field_validator('change_from')
    @classmethod
    def validate(cls, value: str):
        if value not in [const.CHANGE_FROM_USER, const.CHANGE_FROM_TRAINER]:
            raise BadRequestError()
        return value

    @field_validator('change_type')
    @classmethod
    def validate(cls, value: str):
        if value not in [const.CHANGE_TICKET_TYPE_MODIFY, const.CHANGE_TICKET_TYPE_CANCEL]:
            raise BadRequestError()
        return value

    @field_validator('status')
    @classmethod
    def validate(cls, value: str):
        if value not in [const.CHANGE_TICKET_STATUS_APPROVED,
                         const.CHANGE_TICKET_STATUS_REJECTED,
                         const.CHANGE_TICKET_STATUS_CANCELED]:
            raise BadRequestError()
        return value

    @field_validator('change_reason')
    @classmethod
    def validate(cls, value: str):
        return value

    @field_validator('reject_reason')
    @classmethod
    def validate(cls, value: str):
        return value

    @field_validator('start_time')
    @classmethod
    def validate(cls, value: Any):
        return value


class ChangeTicketForTrainer(BaseModel):
    id: int = Field(),
    user_name: str = Field(),
    change_ticket_type: str = Field(),
    as_is_date: str = Field(),
    to_be_date: str = Field(),
    created_at: str = Field(),
    change_ticket_status: str = Field(),
    user_message: str = Field(),
    trainer_message: str = Field()

class ChangeTicketListForTrainer(BaseModel):
    []

class ChangeTicketResponse:
    change_ticket = Model('ChangeTicketList', {
        'change_from': fields.String(),
        'change_type': fields.String(),
        'created_at': fields.String(),
        'description': fields.String(),
        'id': fields.Integer(),
        'reject_reason': fields.String(),
        'request_time': fields.String(),
        'schedule_id': fields.String(),
        'status': fields.String()
    })

    trainer_receive_change_ticket_list = Model('TrainerReceiveChangeTicket', {
        'id': fields.Integer(description='Change Ticket unique identifier'),
        'user_name': fields.String(description='변경티켓을 보낸 유저 이름'),
        'change_ticket_type': fields.String(description='변경티켓 타입. '
                                                        'MODIFY: PT 날짜를 수정하고 싶은 경우'
                                                        'CANCEL: 해당 날짜의 PT를 취소하고 싶은 경우'),
        'as_is_date': fields.String(description='변경 전 날짜'),
        'to_be_date': fields.String(description='변경 희망 날짜'),
        'created_at': fields.String(description='변경티켓 생성 날짜'),
        'change_ticket_status': fields.String(description='변경 티켓 상태. '
                                                          'WAITING: 트레이너의 티켓 처리를 대기중인 상태'
                                                          'APPROVED: 트레이너가 해당 티켓을 수락한 상태'
                                                          'REJECTED: 트레이너가 해당 티켓을 거절한 상태'
                                                          'CANCELED: 유저가 해당 티켓을 취소한 상태'),
        'user_message': fields.String(description='유저의 변경 티켓에 대한 메세지.'),
        'trainer_message': fields.String(description='트레이너의 변경 티켓에 대한 메세지.')
    })

    user_receive_change_ticket_list = Model('UserReceiveChangeTicket', {
        'id': fields.Integer(description='Change Ticket unique identifier'),
        'trainer_name': fields.String(description='변경티켓을 보낸 트레이너의 이름'),
        'change_ticket_type': fields.String(description='변경티켓 타입. '
                                                        'MODIFY: PT 날짜를 수정하고 싶은 경우'
                                                        'CANCEL: 해당 날짜의 PT를 취소하고 싶은 경우'),
        'as_is_date': fields.String(description='변경 전 날짜'),
        'to_be_date': fields.String(description='변경 희망 날짜'),
        'created_at': fields.String(description='변경티켓 생성 날짜'),
        'change_ticket_status': fields.String(description='변경 티켓 상태. '
                                                          'WAITING: 트레이너의 티켓 처리를 대기중인 상태'
                                                          'APPROVED: 트레이너가 해당 티켓을 수락한 상태'
                                                          'REJECTED: 트레이너가 해당 티켓을 거절한 상태'
                                                          'CANCELED: 유저가 해당 티켓을 취소한 상태'),
        'user_message': fields.String(description='유저의 변경 티켓에 대한 메세지.'),
        'trainer_message': fields.String(description='트레이너의 변경 티켓에 대한 메세지.')
    })

    user_send_change_ticket_list = Model('UserSendChangeTicket', {
        'id': fields.Integer(description='Change Ticket unique identifier'),
        'trainer_name': fields.String(description='변경 티켓을 받을 트레이너 이름'),
        'change_ticket_type': fields.String(description='변경티켓 타입. '
                                                        'MODIFY: PT 날짜를 수정하고 싶은 경우'
                                                        'CANCEL: 해당 날짜의 PT를 취소하고 싶은 경우'),
        'as_is_date': fields.String(description='변경 전 날짜'),
        'to_be_date': fields.String(description='변경 희망 날짜'),
        'created_at': fields.String(description='변경티켓 생성 날짜'),
        'change_ticket_status': fields.String(description='변경 티켓 상태. '
                                                          'WAITING: 트레이너의 티켓 처리를 대기중인 상태'
                                                          'APPROVED: 트레이너가 해당 티켓을 수락한 상태'
                                                          'REJECTED: 트레이너가 해당 티켓을 거절한 상태'
                                                          'CANCELED: 유저가 해당 티켓을 취소한 상태'),
        'user_message': fields.String(description='유저의 변경 티켓에 대한 메세지.'),
        'trainer_message': fields.String(description='트레이너의 변경 티켓에 대한 메세지.')
    })
