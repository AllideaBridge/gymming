from app.entities.entity_users import Users
from database import db


class UserRepository:

    @staticmethod
    def select_by_id(user_id):
        return Users.query.filter_by(user_id=user_id).first()

    @staticmethod
    def insert(data):
        db.session.add(data)
        db.session.commit()

    @staticmethod
    def update(user, data):
        user.user_email = data.get('user_email', user.user_email)
        user.user_name = data.get('user_name', user.user_name)
        user.user_gender = data.get('user_gender', user.user_gender)
        user.user_phone_number = data.get('user_phone_number', user.user_phone_number)
        user.user_profile_img_url = data.get('user_profile_img_url', user.user_profile_img_url)
        user.user_delete_flag = data.get('user_delete_flag', user.user_delete_flag)
        user.user_login_platform = data.get('user_login_platform', user.user_login_platform)

        db.session.commit()
        return user

    @staticmethod
    def select_by_social_id(social_id):
        return Users.query.filter_by(user_social_id=social_id).first()

    @staticmethod
    def select_by_username_and_phone_number(user_name: str, phone_number: str):
        return Users.query.filter_by(
            user_name=user_name,
            user_phone_number=phone_number
        ).first()


user_repository = UserRepository()
