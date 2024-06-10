from datetime import datetime

from database import db


class TrainerUser(db.Model):
    trainer_user_id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    lesson_total_count = db.Column(db.Integer, default=0)
    lesson_current_count = db.Column(db.Integer, default=0)
    trainer_user_delete_flag = db.Column(db.Boolean, default=False)
    schedules = db.relationship('Schedule', backref='lesson', lazy='dynamic')
    exercise_days = db.Column(db.String(50), nullable=True)
    special_notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    @staticmethod
    def find_by_id(trainer_user_id):
        return TrainerUser.query.filter_by(trainer_user_id=trainer_user_id).first()

