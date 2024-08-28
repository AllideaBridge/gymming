from flask_sqlalchemy import SQLAlchemy

from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_user import TrainerUser
from app.entities.entity_users import Users
from app.entities.entity_schedule import Schedule
from app.repositories.repository_base import BaseRepository


class TrainerUserRepository(BaseRepository[TrainerUser]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(TrainerUser, db)

    def select_with_users_by_trainer_id(self, trainer_id: int, delete_flag: bool):
        return (self.db.session.query(TrainerUser, Users)
                .join(Users, TrainerUser.user_id == Users.user_id)
                .filter(TrainerUser.trainer_id == trainer_id, TrainerUser.trainer_user_delete_flag == delete_flag)
                .all())

    def select_with_trainers_by_user_id(self, user_id):
        return (self.db.session.query(TrainerUser, Trainer)
                .join(Trainer, TrainerUser.trainer_id == Trainer.trainer_id)
                .filter(TrainerUser.user_id == user_id)
                .all())

    def select_by_trainer_id_and_user_id(self, trainer_id, user_id):
        return TrainerUser.query.filter_by(trainer_id=trainer_id, user_id=user_id).first()
