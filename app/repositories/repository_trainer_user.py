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


trainer_user_repository = TrainerUserRepository()
