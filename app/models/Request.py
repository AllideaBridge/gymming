from database import db


class Request(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.schedule_id'), nullable=False)
    request_from = db.Column(db.String(20), nullable=True)
    request_type = db.Column(db.String(20), nullable=True)
    request_description = db.Column(db.String(255), nullable=True)
    request_status = db.Column(db.String(20), nullable=True)
    request_time = db.Column(db.DateTime, nullable=True)
