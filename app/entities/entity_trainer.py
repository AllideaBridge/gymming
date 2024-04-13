from sqlalchemy import and_, func, literal_column

from app.entities.entity_training_user import TrainingUser
from app.entities.entity_schedule import Schedule
from app.common.constants import SCHEDULE_SCHEDULED
from database import db


class Trainer(db.Model):
    trainer_id = db.Column(db.Integer, primary_key=True)
    center_id = db.Column(db.Integer, db.ForeignKey('center.center_id'), nullable=True)
    trainer_name = db.Column(db.String(20), nullable=False)
    trainer_email = db.Column(db.String(100), nullable=False)
    trainer_gender = db.Column(db.String(5), nullable=False)
    trainer_phone_number = db.Column(db.String(30), nullable=False)
    trainer_pr_url = db.Column(db.String(255), nullable=True)
    trainer_pt_price = db.Column(db.Integer, nullable=True)
    certification = db.Column(db.String(255), nullable=True)
    trainer_education = db.Column(db.String(255), nullable=True)
    trainer_login_platform = db.Column(db.String(20), nullable=True)
    lesson_name = db.Column(db.String(100), nullable=True)
    lesson_price = db.Column(db.Integer, nullable=True)
    lesson_minutes = db.Column(db.Integer, nullable=False)
    lesson_change_range = db.Column(db.Integer, nullable=False)
    trainer_delete_flag = db.Column(db.Boolean, default=False)

    @staticmethod
    def conflict_trainer_schedule(trainer_id, request_time):
        conflict_schedule = db.session.query(Schedule). \
            join(TrainingUser, and_(TrainingUser.training_user_id == Schedule.training_user_id,
                                    Schedule.schedule_status == SCHEDULE_SCHEDULED)). \
            join(Trainer, and_(Trainer.trainer_id == TrainingUser.trainer_id,
                               Trainer.trainer_id == trainer_id)). \
            filter(func.abs(func.timestampdiff(literal_column('MINUTE'), Schedule.schedule_start_time,
                                               request_time)) < Trainer.lesson_minutes). \
            first()

        return conflict_schedule
