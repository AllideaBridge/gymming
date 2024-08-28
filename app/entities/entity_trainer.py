from sqlalchemy import and_, func, literal_column

from app.entities.entity_trainer_user import TrainerUser
from app.entities.entity_schedule import Schedule
from app.common.constants import SCHEDULE_SCHEDULED
from database import db


class Trainer(db.Model):
    trainer_id = db.Column(db.Integer, primary_key=True)
    trainer_social_id = db.Column(db.String(100), nullable=False)
    trainer_name = db.Column(db.String(20), nullable=True)
    trainer_phone_number = db.Column(db.String(30), nullable=True)
    trainer_gender = db.Column(db.String(5), nullable=True)
    trainer_birthday = db.Column(db.Date, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    lesson_name = db.Column(db.String(100), nullable=True)
    lesson_price = db.Column(db.Integer, nullable=True)
    lesson_minutes = db.Column(db.Integer, nullable=True)
    lesson_change_range = db.Column(db.Integer, nullable=True)
    trainer_email = db.Column(db.String(100), nullable=True)
    trainer_delete_flag = db.Column(db.Boolean, default=False)
    center_name = db.Column(db.String(30), nullable=True)
    center_location = db.Column(db.String(100), nullable=True)
    center_number = db.Column(db.String(20), nullable=True)
    center_type = db.Column(db.String(20), nullable=True)
    trainer_users = db.relationship('TrainerUser', backref='trainer', lazy=True)

    @staticmethod
    def conflict_trainer_schedule(trainer_id, request_time):
        conflict_schedule = db.session.query(Schedule). \
            join(TrainerUser, and_(TrainerUser.trainer_user_id == Schedule.trainer_user_id,
                                   Schedule.schedule_status == SCHEDULE_SCHEDULED)). \
            join(Trainer, and_(Trainer.trainer_id == TrainerUser.trainer_id,
                               Trainer.trainer_id == trainer_id)). \
            filter(func.abs(func.timestampdiff(literal_column('MINUTE'), Schedule.schedule_start_time,
                                               request_time)) < Trainer.lesson_minutes). \
            first()

        return conflict_schedule
