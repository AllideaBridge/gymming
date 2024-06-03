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
