from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import coalesce

from app.common.constants import CHANGE_FROM_USER, const
from app.entities.entity_change_ticket import ChangeTicket
from app.entities.entity_schedule import Schedule
from app.entities.entity_users import Users
from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_user import TrainerUser
from app.repositories.repository_base import BaseRepository


class ChangeTicketRepository(BaseRepository[ChangeTicket]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(ChangeTicket, db)

    def select_change_tickets_by_trainer_id(self, trainer_id, status, page=1, per_page=10):
        change_tickets = (self.db.session.query(
            ChangeTicket.id.label('id'),
            Users.user_name.label('user_name'),
            ChangeTicket.change_type.label('change_ticket_type'),
            ChangeTicket.as_is_date.label('as_is_date'),
            ChangeTicket.request_time.label('to_be_date'),
            ChangeTicket.created_at.label('created_at'),
            ChangeTicket.status.label('change_ticket_status'),
            ChangeTicket.description.label('user_message')
        )
                          .join(Schedule, ChangeTicket.schedule_id == Schedule.schedule_id)
                          .join(TrainerUser, Schedule.trainer_user_id == TrainerUser.trainer_user_id)
                          .join(Users, TrainerUser.user_id == Users.user_id)
                          .filter(TrainerUser.trainer_id == trainer_id))

        if status == const.CHANGE_TICKET_STATUS_RESOLVED:
            change_tickets = change_tickets.filter(ChangeTicket.status != const.CHANGE_TICKET_STATUS_WAITING)
        else:
            change_tickets = change_tickets.filter(ChangeTicket.status == status)
        change_tickets = change_tickets.paginate(page=page, per_page=per_page)
        return change_tickets

    def select_change_tickets_by_user_id(self, user_id, status, page=1, per_page=10):
        change_tickets = (self.db.session.query(
            ChangeTicket.id.label('id'),
            Trainer.trainer_name.label('trainer_name'),
            ChangeTicket.change_type.label('change_ticket_type'),
            ChangeTicket.as_is_date.label('as_is_date'),
            ChangeTicket.request_time.label('to_be_date'),
            ChangeTicket.created_at.label('created_at'),
            ChangeTicket.status.label('change_ticket_status'),
            coalesce(ChangeTicket.description, '').label('user_message'),
            coalesce(ChangeTicket.reject_reason, '').label('trainer_message')
        )
                          .join(Schedule, ChangeTicket.schedule_id == Schedule.schedule_id)
                          .join(TrainerUser, Schedule.trainer_user_id == TrainerUser.trainer_user_id)
                          .join(Trainer, TrainerUser.trainer_id == Trainer.trainer_id)
                          .filter(TrainerUser.user_id == user_id))

        if status == const.CHANGE_TICKET_STATUS_RESOLVED:
            change_tickets = change_tickets.filter(ChangeTicket.status != const.CHANGE_TICKET_STATUS_WAITING)
        else:
            change_tickets = change_tickets.filter(ChangeTicket.status == status)
        change_tickets = change_tickets.paginate(page=page, per_page=per_page)
        return change_tickets

    # 유저가 보낸 요청 조회
    def select_user_change_tickets(self, user_id, page=1, per_page=10):
        return (self.db.session.query(
            ChangeTicket.id,
            Trainer.trainer_name,
            ChangeTicket.change_type,
            ChangeTicket.as_is_date,
            ChangeTicket.request_time,
            ChangeTicket.created_at,
            ChangeTicket.status,
            ChangeTicket.description,
            ChangeTicket.reject_reason
        )
                .join(Schedule)
                .join(TrainerUser)
                .join(Trainer)
                .filter(TrainerUser.user_id == user_id, ChangeTicket.change_from == CHANGE_FROM_USER)
                .paginate(page=page, per_page=per_page))

    def select_change_ticket_by_schedule_id(self, schedule_id):
        return ChangeTicket.query.filter_by(schedule_id=schedule_id).first()
