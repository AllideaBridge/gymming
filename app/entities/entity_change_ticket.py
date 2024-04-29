from datetime import datetime

from app.common.constants import REQUEST_STATUS_WAITING
from database import db


class Request(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
class ChangeTicket(db.Model):
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.schedule_id'), nullable=False)
    request_from = db.Column(db.String(20), nullable=True)
    request_type = db.Column(db.String(20), nullable=True)
    request_description = db.Column(db.String(255), nullable=True)
    request_status = db.Column(db.String(20), nullable=True, default=REQUEST_STATUS_WAITING)
    request_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    request_reject_reason = db.Column(db.String(255), nullable=True)