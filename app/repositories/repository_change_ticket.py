from flask_sqlalchemy import SQLAlchemy

from app.common.constants import CHANGE_FROM_USER
from app.entities.entity_change_ticket import ChangeTicket
from app.entities.entity_schedule import Schedule
from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_user import TrainerUser
from app.repositories.repository_base import BaseRepository


class ChangeTicketRepository(BaseRepository[ChangeTicket]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(ChangeTicket, db)

    def select_change_tickets_by_trainer_id(self, trainer_id, status):
        change_tickets = (self.db.session.query(ChangeTicket)
                          .join(Schedule, ChangeTicket.schedule_id == Schedule.schedule_id)
                          .join(TrainerUser, Schedule.trainer_user_id == TrainerUser.trainer_user_id)
                          .filter(TrainerUser.trainer_id == trainer_id, ChangeTicket.status == status).all())
        return change_tickets

    def select_change_tickets_by_user_id(self, user_id, status):
        change_tickets = (self.db.session.query(ChangeTicket)
                          .join(Schedule, ChangeTicket.schedule_id == Schedule.schedule_id)
                          .join(TrainerUser, Schedule.trainer_user_id == TrainerUser.trainer_user_id)
                          .filter(TrainerUser.user_id == user_id, ChangeTicket.status == status).all())
        return change_tickets

    # 유저가 보낸 요청 조회
    def select_user_change_tickets(self, user_id, page=1, per_page=10):
        return (self.db.session.query(
            ChangeTicket.id,
            Trainer.trainer_name,
            ChangeTicket.change_type,
            Schedule.schedule_start_time,
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
