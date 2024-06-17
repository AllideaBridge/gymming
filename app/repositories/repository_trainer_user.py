from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_user import TrainerUser
from app.entities.entity_users import Users
from database import db


class TrainerUserRepository:
    def select_by_id(self, trainer_user_id):
        return TrainerUser.query.filter_by(trainer_user_id=trainer_user_id).first()

    def select_with_users_by_trainer_id(self, trainer_id: int, delete_flag: bool):
        return (db.session.query(TrainerUser, Users)
                .join(Users, TrainerUser.user_id == Users.user_id)
                .filter(TrainerUser.trainer_id == trainer_id, TrainerUser.trainer_user_delete_flag == delete_flag)
                .all())

    def select_with_trainers_by_user_id(self, user_id):
        return (db.session.query(TrainerUser, Trainer)
                .join(Trainer, TrainerUser.trainer_id == Trainer.trainer_id)
                .filter(TrainerUser.user_id == user_id)
                .all())

    def select_by_trainer_id_and_user_id(self, trainer_id, user_id):
        return TrainerUser.query.filter_by(trainer_id=trainer_id, user_id=user_id).first()

    def create_trainer_user(self, new_trainer_user: TrainerUser):
        db.session.add(new_trainer_user)
        db.session.commit()

    def update_trainer_user(self):
        db.session.commit()

trainer_user_repository = TrainerUserRepository()
