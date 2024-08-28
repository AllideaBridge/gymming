from database import db


class Schedule(db.Model):
    schedule_id = db.Column(db.Integer, primary_key=True)
    trainer_user_id = db.Column(db.Integer, db.ForeignKey('trainer_user.trainer_user_id'), nullable=False)
    schedule_start_time = db.Column(db.DateTime)
    schedule_status = db.Column(db.String(20))
    schedule_delete_flag = db.Column(db.Boolean, default=False)
    change_ticket = db.relationship('ChangeTicket', backref='schedule', lazy=True)