from marshmallow import ValidationError

from app.entities.entity_change_ticket import ChangeTicket
from app.repositories.repository_change_ticket import ChangeTicketRepository
from app.repositories.repository_schedule import ScheduleRepository
from app.routes.models.model_change_ticket import CreateChangeTicketRequest


class ChangeTicketService:
    def __init__(self):
        self.change_ticket_repository = ChangeTicketRepository()
        self.schedule_repository = ScheduleRepository()
        pass

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

    def update_change_ticket(self):
        pass
