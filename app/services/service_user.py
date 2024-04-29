from app.entities.entity_users import Users
from app.repositories.repository_users import user_repository
from database import db


class UserService:

    @staticmethod
    def get_user(user_id):
        return user_repository.select_by_id(user_id)

    @staticmethod
    def create_user(data):
        new_user = Users(
            user_email=data['user_email'],
            user_name=data.get('user_name'),
            user_gender=data.get('user_gender'),
            user_phone_number=data.get('user_phone_number'),
            user_profile_img_url=data.get('user_profile_img_url'),
            user_delete_flag=data.get('user_delete_flag', False),
            user_login_platform=data['user_login_platform']
        )
        user_repository.insert(new_user)
        return new_user

    @staticmethod
    def update_user(user, data):
        return user_repository.update(user, data)


user_service = UserService()
