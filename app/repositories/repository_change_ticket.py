from app.entities.entity_change_ticket import ChangeTicket
from database import db


class ChangeTicketRepository:
    def __int__(self):
        pass

    def insert_change_ticket(self, data: ChangeTicket):
        db.session.add(data)
        db.session.commit()
