from app.entities.entity_user_fcm_token import UserFcmToken
from app.entities.entity_users import Users

from database import db


class UserService:
    def __init__(self, user_repository, user_fcm_repository):
        self.user_repository = user_repository
        self.user_fcm_repository = user_fcm_repository

    def get_user(self, user_id):
        return self.user_repository.get(user_id)

    def create_user(self, data):
        new_user = Users(
            user_social_id=data['user_social_id'],
            user_email=data.get('user_email'),
            user_name=data.get('user_name'),
            user_gender=data.get('user_gender'),
            user_phone_number=data.get('user_phone_number'),
            user_delete_flag=data.get('user_delete_flag', False),
        )
        self.user_repository.create(new_user)
        return new_user

    def update_user(self, user, data):
        user.user_email = data.get('user_email', user.user_email)
        user.user_name = data.get('user_name', user.user_name)
        user.user_gender = data.get('user_gender', user.user_gender)
        user.user_phone_number = data.get('user_phone_number', user.user_phone_number)
        user.user_profile_img_url = data.get('user_profile_img_url', user.user_profile_img_url)
        user.user_delete_flag = data.get('user_delete_flag', user.user_delete_flag)
        user.user_birthday = data.get('user_birthday', user.user_birthday)

        return self.user_repository.update(user)

    def get_user_by_social_id(self, social_id):
        return self.user_repository.select_by_social_id(social_id)

    def create_user_only_social_id(self, social_id):
        new_user = Users(
            user_social_id=social_id
        )
        self.user_repository.create(new_user)
        return new_user

    def check_user_exists(self, user_name, user_phone_number):
        user = self.user_repository.select_by_username_and_phone_number(user_name, user_phone_number)

        if user:
            return {
                "id": user.user_id,
                "email": user.user_email,
                "name": user.user_name,
                "gender": user.user_gender,
                "phone_number": user.user_phone_number,
                "user_profile_img_url": None,
                "delete_flag": user.user_delete_flag,
                "birthday": user.user_birthday
            }

        return None;

    def create_user_fcm_token(self, user_id, body):
        old_token = self.user_fcm_repository.get_by_user_id(user_id=user_id)
        if old_token is not None:
            self.user_fcm_repository.delete(old_token)

        user_fcm_token = UserFcmToken(
            user_id=user_id,
            fcm_token=body.fcm_token
        )

        self.user_fcm_repository.create(user_fcm_token)
