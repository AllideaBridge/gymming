from datetime import datetime

from app.common.constants import CHANGE_TICKET_STATUS_WAITING
from database import db


class ChangeTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.schedule_id'), nullable=False)
    change_from = db.Column(db.String(20), nullable=True)
    change_type = db.Column(db.String(20), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=True, default=CHANGE_TICKET_STATUS_WAITING)
    request_time = db.Column(db.DateTime, nullable=True)
    as_is_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reject_reason = db.Column(db.String(255), nullable=True)

    def __init__(self, schedule_id=None,
                 change_from=None,
                 change_type=None,
                 description=None,
                 status=CHANGE_TICKET_STATUS_WAITING,
                 request_time=None,
                 reject_reason=None,
                 as_is_date=None):
        self.schedule_id = schedule_id
        self.change_from = change_from
        self.change_type = change_type
        self.description = description
        self.status = status
        self.request_time = request_time
        self.created_at = datetime.utcnow()
        self.reject_reason = reject_reason
        self.as_is_date = as_is_date

    def to_dict(self):
        return {
            'id': self.id,
            'schedule_id': self.schedule_id,
            'change_from': self.change_from,
            'change_type': self.change_type,
            'description': self.description,
            'status': self.status,
            'request_time': self.request_time.isoformat() if self.request_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reject_reason': self.reject_reason
        }
