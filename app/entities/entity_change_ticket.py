from datetime import datetime

from app.common.constants import REQUEST_STATUS_WAITING
from database import db


class ChangeTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.schedule_id'), nullable=False)
    change_from = db.Column(db.String(20), nullable=True)
    change_type = db.Column(db.String(20), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=True, default=REQUEST_STATUS_WAITING)
    request_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reject_reason = db.Column(db.String(255), nullable=True)
