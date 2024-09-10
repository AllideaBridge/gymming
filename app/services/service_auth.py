# auth_service.py
from http import HTTPStatus

import requests

from app.common.exceptions import BadRequestError
from app.services.service_factory import ServiceFactory
from app.services.service_user import UserService


class AuthService:
    def __init__(self):
        self.kakao_token_verify_url = 'https://kapi.kakao.com/v1/user/access_token_info'
        self.kakao_get_user_info_url = 'https://kapi.kakao.com/v2/user/me'
        self.trainer_service = ServiceFactory.trainer_service()
        self.user_service = ServiceFactory.user_service()

    def verify_kakao_token(self, token):
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(self.kakao_token_verify_url, headers=headers)

        if response.status_code != HTTPStatus.OK:
            return False, None

        return True, response.json()

    def get_kakao_user_info(self, token):
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(self.kakao_get_user_info_url, headers=headers)

        if response.status_code != HTTPStatus.OK:
            return None

        return response.json()

    def authenticate_kakao_user(self, token):
        is_valid, _ = self.verify_kakao_token(token)
        if not is_valid:
            raise BadRequestError(message="유효한 토큰이 아닙니다.")

        kakao_user_info = self.get_kakao_user_info(token)
        if kakao_user_info is None:
            raise BadRequestError(message="카카오 서비스 이상. 다시 요청해주세요.")

        kakao_unique_id = kakao_user_info.get('id')
        social_id = f'kakao{kakao_unique_id}'

        return social_id

    def auth_gymming_kakao_user(self, token):
        social_id = self.authenticate_kakao_user(token)
        user = self.user_service.get_user_by_social_id(social_id)
        return user

    def auth_gymming_kakao_trainer(self, token):
        social_id = self.authenticate_kakao_user(token)
        trainer = self.trainer_service.get_trainer_by_social_id(social_id)
        return trainer
