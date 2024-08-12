from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

from app.entities.entity_user_fcm_token import UserFcmToken
from app.repositories.repository_base import BaseRepository


class UserFcmTokenRepository(BaseRepository[UserFcmToken]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(UserFcmToken, db)

    def get_by_user_id(self, user_id):
        return UserFcmToken.query.filter_by(user_id=user_id).first()
