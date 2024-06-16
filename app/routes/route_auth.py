from datetime import datetime, timedelta
from http import HTTPStatus

from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, \
    create_refresh_token, decode_token
from flask_restx import Namespace, Resource

from app.common.exceptions import BadRequestError
from app.services.service_auth import AuthService
from app.services.service_token import TokenService

ns_auth = Namespace('auth', description='auth api', path='/auth')


@ns_auth.route("/kakao/user")
class UserKakaoAuthResource(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_service = TokenService()
        self.auth_service = AuthService()

    def post(self):
        body = request.get_json()
        token = body.get('kakao_token')
        if token is None:
            raise BadRequestError(message="소셜 로그인 토큰이 필요합니다.")

        user = self.auth_service.auth_gymming_kakao_user(token)

        identity = {"user_id": user.user_id}
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        print(len(refresh_token))
        self.token_service.insert_user_token(user.user_id, refresh_token)

        return {
            "user_id": user.user_id,
            "access_token": access_token,
            "refresh_token": refresh_token
        }, HTTPStatus.OK


@ns_auth.route("/kakao/trainer")
class TrainerKakaoAuthResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_service = TokenService()
        self.auth_service = AuthService()

    def post(self):
        body = request.get_json()
        token = body.get('kakao_token')
        if token is None:
            raise BadRequestError(message="소셜 로그인 토큰이 필요합니다.")

        trainer = self.auth_service.auth_gymming_kakao_trainer(token)

        identity = {"trainer_id": trainer.trainer_id}
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        self.token_service.insert_trainer_token(trainer.trainer_id, refresh_token)

        return {
            "trainer_id": trainer.trainer_id,
            "access_token": access_token,
            "refresh_token": refresh_token
        }, HTTPStatus.OK


@ns_auth.route("/refresh")
class RefreshAuthResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_service = TokenService()

    @jwt_required(refresh=True)
    def get(self):
        current_user = get_jwt_identity()
        refresh_token = request.headers.get('Authorization').split()[1]

        if 'trainer_id' in current_user:
            trainer_token = self.token_service.get_trainer_token(current_user['trainer_id'])
            if not trainer_token or trainer_token.refresh_token != refresh_token:
                return {"message": "Invalid refresh token"}, HTTPStatus.UNAUTHORIZED,
        elif 'user_id' in current_user:
            user_token = self.token_service.get_user_token(current_user['user_id'])
            if not user_token or user_token.refresh_token != refresh_token:
                return {"message": "Invalid refresh token"}, HTTPStatus.UNAUTHORIZED
        else:
            return {"message": "Invalid refresh token"}, HTTPStatus.UNAUTHORIZED

        decoded_token = decode_token(refresh_token)
        token_expiry = datetime.utcfromtimestamp(decoded_token['exp'])

        new_access_token = create_access_token(identity=current_user)

        new_refresh_token = None
        if token_expiry - datetime.utcnow() < timedelta(days=7):
            new_refresh_token = create_refresh_token(identity=current_user)
            if 'trainer_id' in current_user:
                self.token_service.insert_trainer_token(current_user['trainer_id'], new_refresh_token)
            elif 'user_id' in current_user:
                self.token_service.insert_user_token(current_user['user_id'], new_refresh_token)

        response = {"access_token": new_access_token, "refresh_token": None}
        if new_refresh_token:
            response["refresh_token"] = new_refresh_token

        return response, HTTPStatus.OK
