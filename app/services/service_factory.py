from app.repositories.repository_user_fcm_token import UserFcmTokenRepository
from app.repositories.repository_users import UserRepository
from app.services.service_user import UserService
from database import db


class ServiceFactory:
    @staticmethod
    def user_service():
        return UserService(
            user_repository=UserRepository(db=db),
            user_fcm_repository=UserFcmTokenRepository(db=db)
        )
