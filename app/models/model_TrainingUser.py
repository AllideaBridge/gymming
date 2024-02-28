from database import db


class TrainingUser(db.Model):
    training_user_id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    lesson_total_count = db.Column(db.Integer, nullable=True)
    lesson_current_count = db.Column(db.Integer, nullable=True)
    training_user_delete_flag = db.Column(db.Boolean, default=False)
    schedules = db.relationship('Schedule', backref='lesson', lazy='dynamic')
