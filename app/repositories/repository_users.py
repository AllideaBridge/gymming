from flask_sqlalchemy import SQLAlchemy

from app.entities.entity_users import Users
from app.repositories.repository_base import BaseRepository


class UserRepository(BaseRepository[Users]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(Users, db)

    def select_by_social_id(self, social_id):
        return Users.query.filter_by(user_social_id=social_id).first()

    def select_by_username_and_phone_number(self, user_name: str, phone_number: str):
        return Users.query.filter_by(
            user_name=user_name,
            user_phone_number=phone_number
        ).first()
