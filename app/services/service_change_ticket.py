from marshmallow import ValidationError

from app.common.constants import CHANGE_TICKET_STATUS_APPROVED, CHANGE_TICKET_STATUS_REJECTED, CHANGE_FROM_USER, \
    CHANGE_FROM_TRAINER, SCHEDULE_MODIFIED, CHANGE_TICKET_TYPE_MODIFY, CHANGE_TICKET_STATUS_CANCELED
from app.common.exceptions import ApplicationError
from app.entities.entity_change_ticket import ChangeTicket
from app.entities.entity_schedule import Schedule
from app.entities.entity_trainer import Trainer
from app.entities.entity_training_user import TrainingUser
from app.entities.entity_users import Users
from app.repositories.repository_change_ticket import ChangeTicketRepository
from app.repositories.repository_schedule import ScheduleRepository
from app.repositories.repository_training_user import TrainingUserRepository
from app.repositories.repository_users import UserRepository
from app.routes.models.model_change_ticket import CreateChangeTicketRequest, UpdateChangeTicketRequest
from app.services.service_schedule import ScheduleService


class ChangeTicketService:
    def __init__(self):
        self.change_ticket_repository = ChangeTicketRepository()
        self.schedule_repository = ScheduleRepository()
        self.schedule_service = ScheduleService()
        self.user_repository = UserRepository()
        self.trainer_user_repository = TrainingUserRepository()

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
        elif data.status == CHANGE_TICKET_STATUS_CANCELED:
            pass

        self.change_ticket_repository.update_change_ticket()

    def delete_change_ticket(self, change_ticket_id):
        change_ticket = self.change_ticket_repository.select_change_ticket_by_id(change_ticket_id)
        if not change_ticket:
            raise ApplicationError(f"존재하지 않는 change ticket {change_ticket_id}", 400)

        self.change_ticket_repository.delete_change_ticket(change_ticket)

    def get_change_ticket_list_by_trainer(self, trainer_id, status, page):
        change_tickets = self.change_ticket_repository.select_change_tickets_by_trainer_id(trainer_id, status)

        results = []
        for ticket in change_tickets:
            schedule: Schedule = self.schedule_repository.select_by_id(ticket.schedule_id)
            trainer_user: TrainingUser = self.trainer_user_repository.select_by_id(schedule.training_user_id)
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
            trainer_user: TrainingUser = self.trainer_user_repository.select_by_id(schedule.training_user_id)
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
