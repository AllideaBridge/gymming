from marshmallow import ValidationError

from app.common.constants import CHANGE_TICKET_STATUS_APPROVED, CHANGE_TICKET_STATUS_REJECTED, CHANGE_FROM_USER, \
    CHANGE_FROM_TRAINER, SCHEDULE_MODIFIED
from app.common.exceptions import ApplicationError
from app.entities.entity_change_ticket import ChangeTicket
from app.repositories.repository_change_ticket import ChangeTicketRepository
from app.repositories.repository_schedule import ScheduleRepository
from app.routes.models.model_change_ticket import CreateChangeTicketRequest, UpdateChangeTicketRequest
from app.services.service_schedule import ScheduleService


class ChangeTicketService:
    def __init__(self):
        self.change_ticket_repository = ChangeTicketRepository()
        self.schedule_repository = ScheduleRepository()
        self.schedule_service = ScheduleService()
        pass
    def get_change_ticket_by_id(self, change_ticket_id) -> ChangeTicket:
        return self.change_ticket_repository.select_change_ticket_by_id(change_ticket_id)

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

    def _approve_change_ticket(self, change_ticket_id, data: UpdateChangeTicketRequest):
        change_ticket = self.change_ticket_repository.select_change_ticket_by_id(change_ticket_id)

        if data.change_from == CHANGE_FROM_TRAINER:
            self.schedule_service.handle_change_user_schedule(change_ticket.schedule_id, data.start_time, SCHEDULE_MODIFIED)
        elif data.change_from == CHANGE_FROM_USER:
            self.schedule_service.handle_change_trainer_schedule(change_ticket.schedule_id, data.start_time, SCHEDULE_MODIFIED)

    def handle_update_change_ticket(self, change_ticket_id, data: UpdateChangeTicketRequest):
        change_ticket_to_update = self.change_ticket_repository.select_change_ticket_by_id(change_ticket_id)
        if not change_ticket_to_update:
            raise ApplicationError(f"존재하지 않는 change ticket {change_ticket_id}", 400)

        change_ticket_to_update.description = data.change_reason
        change_ticket_to_update.status = data.status

        if data.status == CHANGE_TICKET_STATUS_APPROVED:
            self._approve_change_ticket(change_ticket_id, data)
        elif data.status == CHANGE_TICKET_STATUS_REJECTED:
            change_ticket_to_update.reject_reason = data.reject_reason

        self.change_ticket_repository.update_change_ticket(change_ticket_to_update)

    def delete_change_ticket(self, change_ticket_id):
        change_ticket = self.change_ticket_repository.select_change_ticket_by_id(change_ticket_id)
        if not change_ticket:
            raise ApplicationError(f"존재하지 않는 change ticket {change_ticket_id}", 400)

        self.change_ticket_repository.delete_change_ticket(change_ticket)
