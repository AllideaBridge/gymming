from app.entities.entity_schedule import Schedule
from app.entities.entity_trainer_user import TrainerUser
from app.entities.entity_change_ticket import ChangeTicket
from database import db


class ChangeTicketRepository:
    def __int__(self):
        pass

    def select_change_ticket_by_id(self, change_ticket_id) -> ChangeTicket:
        return db.session.query(ChangeTicket).filter_by(id=change_ticket_id).first()

    def insert_change_ticket(self, data: ChangeTicket):
        db.session.add(data)
        db.session.commit()

    def update_change_ticket(self):
        db.session.commit()

    def delete_change_ticket(self, change_ticket: ChangeTicket):
        db.session.delete(change_ticket)
        db.session.commit()

    def select_change_tickets_by_trainer_id(self, trainer_id, status):
        change_tickets = (db.session.query(ChangeTicket)
                          .join(Schedule, ChangeTicket.schedule_id == Schedule.schedule_id)
                          .join(TrainerUser, Schedule.trainer_user_id == TrainerUser.trainer_user_id)
                          .filter(TrainerUser.trainer_id == trainer_id, ChangeTicket.status == status).all())
        return change_tickets

    def select_change_tickets_by_user_id(self, user_id, status):
        change_tickets = (db.session.query(ChangeTicket)
                          .join(Schedule, ChangeTicket.schedule_id == Schedule.schedule_id)
                          .join(TrainerUser, Schedule.trainer_user_id == TrainerUser.trainer_user_id)
                          .filter(TrainerUser.user_id == user_id, ChangeTicket.status == status).all())
        return change_tickets
