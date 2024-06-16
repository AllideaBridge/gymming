from app.entities.entity_trainer_refresh_token import TrainerRefreshToken
from app.entities.entity_user_refresh_token import UserRefreshToken
from database import db


class TokenRepository:

    def select_user_refresh_token_by_user_id(self, user_id):
        return UserRefreshToken.query.filter_by(user_id=user_id).first()

    def select_trainer_refresh_token_by_trainer_id(self, trainer_id):
        return TrainerRefreshToken.query.filter_by(trainer_id=trainer_id).first()

    def insert_user_refresh_token(self, user_id, refresh_token):
        user_token = UserRefreshToken(
            user_id=user_id,
            refresh_token=refresh_token
        )
        db.session.add(user_token)
        db.session.commit()

    def insert_trainer_refresh_token(self, trainer_id, refresh_token):
        trainer_token = TrainerRefreshToken(
            trainer_id=trainer_id,
            refresh_token=refresh_token
        )
        db.session.add(trainer_token)
        db.session.commit()

    def update(self, token, refresh_token):
        token.refresh_token = refresh_token
        db.session.add(token)
        db.session.commit()
