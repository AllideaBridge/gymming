from database import db


class Schedule(db.Model):
    schedule_id = db.Column(db.Integer, primary_key=True)
    training_user_id = db.Column(db.Integer, db.ForeignKey('training_user.training_user_id'), nullable=False)
    schedule_start_time = db.Column(db.DateTime)
    schedule_status = db.Column(db.String(20))
    schedule_delete_flag = db.Column(db.Boolean, default=False)
