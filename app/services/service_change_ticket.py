from marshmallow import ValidationError

from app.common.constants import CHANGE_TICKET_STATUS_APPROVED, CHANGE_TICKET_STATUS_REJECTED, \
    CHANGE_TICKET_TYPE_MODIFY, CHANGE_TICKET_STATUS_CANCELED, DATETIMEFORMAT, SCHEDULE_MODIFIED, SCHEDULE_CANCELLED, \
    CHANGE_TICKET_STATUS_WAITING, const
from app.common.exceptions import ApplicationError, BadRequestError
from app.entities.entity_change_ticket import ChangeTicket
from app.entities.entity_schedule import Schedule
from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_user import TrainerUser
from app.entities.entity_users import Users
from app.models.model_change_ticket import CreateChangeTicketRequest, UpdateChangeTicketRequest


class ChangeTicketService:
    def __init__(self, change_ticket_repository, schedule_repository, schedule_service, user_repository,
                 trainer_user_repository, trainer_repository, message_service, user_fcm_token_repository):
        self.change_ticket_repository = change_ticket_repository
        self.schedule_repository = schedule_repository
        self.schedule_service = schedule_service
        self.user_repository = user_repository
        self.trainer_user_repository = trainer_user_repository
        self.trainer_repository = trainer_repository
        self.message_service = message_service
        self.user_fcm_token_repository = user_fcm_token_repository

    def get_change_ticket_by_id(self, change_ticket_id) -> ChangeTicket:
        result = self.change_ticket_repository.get(change_ticket_id)
        if not result:
            raise BadRequestError(message=f"존재하지 않는 Change Ticket 입니다. {change_ticket_id}")
        return result

    def create_change_ticket(self, data: CreateChangeTicketRequest):
        schedule = self.schedule_repository.get(data.schedule_id)
        if schedule is None:
            raise ValidationError(message=f'SCHEDULE_ID NOT FOUND: {data.schedule_id}')

        change_ticket = self.change_ticket_repository.select_change_ticket_by_schedule_id(
            schedule_id=schedule.schedule_id)

        if change_ticket is not None:
            raise BadRequestError(message='이미 스케쥴 변경 요청이 있습니다.')

        new_change_ticket = ChangeTicket(
            schedule_id=data.schedule_id,
            change_from=data.change_from,
            change_type=data.change_type,
            description=data.change_reason,
            request_time=data.start_time,
            as_is_date=data.as_is_date
        )
        self.change_ticket_repository.create(new_change_ticket)
        return True

    def handle_update_change_ticket(self, change_ticket_id, data: UpdateChangeTicketRequest):
        change_ticket_to_update = self.change_ticket_repository.get(change_ticket_id)
        if not change_ticket_to_update:
            raise ApplicationError(f"존재하지 않는 change ticket {change_ticket_id}", 400)
        if change_ticket_to_update.status != CHANGE_TICKET_STATUS_WAITING:
            raise ApplicationError(f"이미 처리된 Change Ticket 입니다. {change_ticket_id}", 400)

        # 요청 승인은 트레이너가 하는 것.
        if data.status == CHANGE_TICKET_STATUS_APPROVED:
            if change_ticket_to_update.change_type == const.CHANGE_TICKET_TYPE_CANCEL:
                self.schedule_service.handle_change_user_schedule(
                    change_ticket_to_update.schedule_id, data.start_time, SCHEDULE_CANCELLED)
            elif change_ticket_to_update.change_type == const.CHANGE_TICKET_TYPE_MODIFY:
                self.schedule_service.handle_change_user_schedule(
                    change_ticket_to_update.schedule_id, data.start_time, SCHEDULE_MODIFIED)
        # 요청 취소는 유저가 하는 것.
        elif data.status == CHANGE_TICKET_STATUS_CANCELED:
            self.schedule_service.handle_change_user_schedule(
                change_ticket_to_update.schedule_id, data.start_time, SCHEDULE_CANCELLED)
        # 요청 거절은 트레이너가 하는 것.
        elif data.status == CHANGE_TICKET_STATUS_REJECTED:
            change_ticket_to_update.reject_reason = data.reject_reason

        change_ticket_to_update.description = data.change_reason
        change_ticket_to_update.status = data.status

        self.change_ticket_repository.update(change_ticket_to_update)

        # 유저에게 푸쉬알림 전송
        if data.status in [CHANGE_TICKET_STATUS_APPROVED, CHANGE_TICKET_STATUS_REJECTED]:
            change_ticket_result = '승인'
            if data.status == CHANGE_TICKET_STATUS_REJECTED:
                change_ticket_result = '거절'

            lesson = change_ticket_to_update.schedule.lesson
            trainer = lesson.trainer
            user_fcm_token = self.user_fcm_token_repository.get_by_user_id(user_id=lesson.user_id)
            data = {
                'change_ticket': change_ticket_to_update
            }
            self.message_service.send_message(title=f'요청 {change_ticket_result}',
                                              body=f'{trainer.trainer_name}님이 요청을 {change_ticket_result}하였습니다.',
                                              token=user_fcm_token.fcm_token, data=data)

    def delete_change_ticket(self, change_ticket_id):
        change_ticket = self.change_ticket_repository.get(change_ticket_id)
        if not change_ticket:
            raise ApplicationError(f"존재하지 않는 change ticket {change_ticket_id}", 400)

        if change_ticket.status != CHANGE_TICKET_STATUS_WAITING:
            raise BadRequestError(message='이미 결정된 티켓은 철회할 수 없습니다.')

        self.change_ticket_repository.delete(change_ticket)

    def get_change_ticket_list_by_trainer(self, trainer_id, status, page):
        if not self.trainer_repository.get(trainer_id):
            raise BadRequestError("존재하지 않는 트레이너 입니다.")
        change_tickets = self.change_ticket_repository.select_change_tickets_by_trainer_id(trainer_id, status,
                                                                                           page=page)

        results = []
        for ticket in change_tickets:
            result = {
                'id': ticket.id,
                'user_name': ticket.user_name,
                'change_ticket_type': ticket.change_ticket_type,
                'as_is_date': ticket.as_is_date,
                'to_be_date': ticket.to_be_date if ticket.change_ticket_type == CHANGE_TICKET_TYPE_MODIFY else None,
                'created_at': ticket.created_at,
                'change_ticket_status': ticket.change_ticket_status,
                'user_message': ticket.user_message,
                'trainer_message': None
            }
            results.append(result)

        return results

    def get_change_ticket_list_by_user(self, user_id, status, page):
        change_tickets = self.change_ticket_repository.select_change_tickets_by_user_id(user_id, status, page)

        results = []
        for ticket in change_tickets:
            result = {
                'id': ticket.id,
                'trainer_name': ticket.trainer_name,
                'change_ticket_type': ticket.change_ticket_type,
                'as_is_date': ticket.as_is_date,
                'to_be_date': ticket.to_be_date if ticket.change_ticket_type == CHANGE_TICKET_TYPE_MODIFY else None,
                'created_at': ticket.created_at,
                'change_ticket_status': ticket.change_ticket_status,
                'user_message': None,
                'trainer_message': ticket.trainer_message
            }
            results.append(result)

        return results

    def get_user_change_ticket_history(self, user_id, page=None):
        change_tickets = self.change_ticket_repository.select_user_change_tickets(user_id, page)
        return [{
            "id": ticket.id,
            "trainer_name": ticket.trainer_name,
            "change_ticket_type": ticket.change_type,
            "as_is_date": ticket.as_is_date.strftime(DATETIMEFORMAT),
            "to_be_date": ticket.request_time.strftime(DATETIMEFORMAT),
            "created_at": ticket.created_at.strftime(DATETIMEFORMAT),
            "change_ticket_status": ticket.status,
            "user_message": ticket.description,
            "trainer_message": ticket.reject_reason
        } for ticket in change_tickets]
