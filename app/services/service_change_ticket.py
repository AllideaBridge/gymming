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
from app.repositories.repository_change_ticket import ChangeTicketRepository
from app.repositories.repository_schedule import ScheduleRepository
from app.repositories.repository_trainer import TrainerRepository
from app.repositories.repository_trainer_user import TrainerUserRepository
from app.repositories.repository_users import UserRepository
from app.routes.models.model_change_ticket import CreateChangeTicketRequest, UpdateChangeTicketRequest
from app.services.service_schedule import ScheduleService


class ChangeTicketService:
    def __init__(self):
        self.change_ticket_repository = ChangeTicketRepository()
        self.schedule_repository = ScheduleRepository()
        self.schedule_service = ScheduleService()
        self.user_repository = UserRepository()
        self.trainer_user_repository = TrainerUserRepository()
        self.trainer_repository = TrainerRepository()

    def get_change_ticket_by_id(self, change_ticket_id) -> ChangeTicket:
        result = self.change_ticket_repository.select_change_ticket_by_id(change_ticket_id)
        if not result:
            raise BadRequestError(message=f"존재하지 않는 Change Ticket 입니다. {change_ticket_id}")
        return result

    def create_change_ticket(self, data: CreateChangeTicketRequest):
        if self.schedule_repository.select_schedule_by_id(data.schedule_id) is None:
            raise ValidationError(message=f'SCHEDULE_ID NOT FOUND: {data.schedule_id}')

        new_change_ticket = ChangeTicket(
            schedule_id=data.schedule_id,
            change_from=data.change_from,
            change_type=data.change_type,
            description=data.change_reason,
            request_time=data.start_time
        )
        self.change_ticket_repository.insert_change_ticket(new_change_ticket)
        return True

    def handle_update_change_ticket(self, change_ticket_id, data: UpdateChangeTicketRequest):
        change_ticket_to_update = self.change_ticket_repository.select_change_ticket_by_id(change_ticket_id)
        if not change_ticket_to_update:
            raise ApplicationError(f"존재하지 않는 change ticket {change_ticket_id}", 400)
        if change_ticket_to_update.status != CHANGE_TICKET_STATUS_WAITING:
            raise ApplicationError(f"이미 처리된 Change Ticket 입니다. {change_ticket_id}", 400)

        if data.status == CHANGE_TICKET_STATUS_APPROVED:
            if change_ticket_to_update.change_type == const.CHANGE_TICKET_TYPE_CANCEL:
                self.schedule_service.handle_change_user_schedule(
                    change_ticket_to_update.schedule_id, data.start_time, SCHEDULE_CANCELLED)
            elif change_ticket_to_update.change_type == const.CHANGE_TICKET_TYPE_MODIFY:
                self.schedule_service.handle_change_user_schedule(
                    change_ticket_to_update.schedule_id, data.start_time, SCHEDULE_MODIFIED)
        elif data.status == CHANGE_TICKET_STATUS_CANCELED:
            self.schedule_service.handle_change_user_schedule(
                change_ticket_to_update.schedule_id, data.start_time, SCHEDULE_CANCELLED)
        elif data.status == CHANGE_TICKET_STATUS_REJECTED:
            change_ticket_to_update.reject_reason = data.reject_reason

        change_ticket_to_update.description = data.change_reason
        change_ticket_to_update.status = data.status

        self.change_ticket_repository.update_change_ticket()

    def delete_change_ticket(self, change_ticket_id):
        change_ticket = self.change_ticket_repository.select_change_ticket_by_id(change_ticket_id)
        if not change_ticket:
            raise ApplicationError(f"존재하지 않는 change ticket {change_ticket_id}", 400)

        self.change_ticket_repository.delete_change_ticket(change_ticket)

    def get_change_ticket_list_by_trainer(self, trainer_id, status, page):
        if not self.trainer_repository.select_trainer_by_id(trainer_id):
            raise BadRequestError("존재하지 않는 트레이너 입니다.")
        change_tickets = self.change_ticket_repository.select_change_tickets_by_trainer_id(trainer_id, status)

        results = []
        for ticket in change_tickets:
            schedule: Schedule = self.schedule_repository.select_by_id(ticket.schedule_id)
            trainer_user: TrainerUser = self.trainer_user_repository.select_by_id(schedule.trainer_user_id)
            user: Users = self.user_repository.select_by_id(user_id=trainer_user.user_id)
            result = {
                'id': ticket.id,
                'user_name': user.user_name,
                'change_ticket_type': ticket.change_type,
                'as_is_date': schedule.schedule_start_time,
                'to_be_date': ticket.request_time if ticket.change_type == CHANGE_TICKET_TYPE_MODIFY else None,
                'created_at': ticket.created_at,
                'change_ticket_status': ticket.status,
                'user_message': ticket.description,
                'trainer_message': None
            }
            results.append(result)

        return results

    def get_change_ticket_list_by_user(self, user_id, status, page):
        change_tickets = self.change_ticket_repository.select_change_tickets_by_user_id(user_id, status)

        results = []
        for ticket in change_tickets:
            schedule: Schedule = self.schedule_repository.select_by_id(ticket.schedule_id)
            trainer_user: TrainerUser = self.trainer_user_repository.select_by_id(schedule.trainer_user_id)
            # TODO: trainer 에 대한 repository 구현 완료 시 Repository 사용하도록 변경
            trainer: Trainer = Trainer.query.filter_by(trainer_id=trainer_user.trainer_id).first()
            result = {
                'id': ticket.id,
                'user_name': trainer.trainer_name,
                'change_ticket_type': ticket.change_type,
                'as_is_date': schedule.schedule_start_time,
                'to_be_date': ticket.request_time if ticket.change_type == CHANGE_TICKET_TYPE_MODIFY else None,
                'created_at': ticket.created_at,
                'change_ticket_status': ticket.status,
                'user_message': None,
                'trainer_message': ticket.description
            }
            results.append(result)

        return results

    def get_user_change_ticket_history(self, user_id, page=None):
        change_tickets = self.change_ticket_repository.select_user_change_tickets(user_id, page)
        return [{
            "id": ticket.id,
            "trainer_name": ticket.trainer_name,
            "change_ticket_type": ticket.change_type,
            "as_is_date": ticket.schedule_start_time.strftime(DATETIMEFORMAT),
            "to_be_date": ticket.request_time.strftime(DATETIMEFORMAT),
            "created_at": ticket.created_at.strftime(DATETIMEFORMAT),
            "change_ticket_status": ticket.status,
            "user_message": ticket.description,
            "trainer_message": ticket.reject_reason
        } for ticket in change_tickets]
