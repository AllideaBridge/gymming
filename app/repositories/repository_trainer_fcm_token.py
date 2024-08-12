from flask_sqlalchemy import SQLAlchemy

from app.entities.entity_trainer_fcm_token import TrainerFcmToken
from app.repositories.repository_base import BaseRepository


class TrainerFcmTokenRepository(BaseRepository[TrainerFcmToken]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(TrainerFcmToken, db)

    def get_by_trainer_id(self, trainer_id):
        return TrainerFcmToken.query.filter_by(trainer_id=trainer_id).first()
