from datetime import datetime, timedelta
from http import HTTPStatus

from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, \
    create_refresh_token, decode_token
from flask_pydantic import validate
from flask_restx import Namespace, Resource

from app.common.exceptions import BadRequestError, UnAuthorizedError
from app.models.model_auth import KakaoAuthRequest, KakaoUserRegisterRequest, KakaoTrainerRegisterRequest
from app.services.service_auth import AuthService
from app.services.service_factory import ServiceFactory
from app.services.service_token import TokenService

ns_auth = Namespace('auth', description='auth api', path='/auth')


@ns_auth.route("/register/kakao/user")
class UserKakaoRegisterResource(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_service = TokenService()
        self.auth_service = AuthService()
        self.user_service = ServiceFactory.user_service()

    @validate()
    def post(self, body: KakaoUserRegisterRequest):
        user_social_id = self.auth_service.authenticate_kakao_user(body.kakao_token)
        user = self.user_service.get_user_by_social_id(user_social_id)
        if user:
            raise BadRequestError(message='이미 존재하는 회원입니다.')

        data = body.__dict__
        data['user_social_id'] = user_social_id
        user = self.user_service.create_user(data)

        identity = {"user_id": user.user_id}
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        self.token_service.insert_user_token(user.user_id, refresh_token)

        return {
            "user_id": user.user_id,
            "access_token": access_token,
            "refresh_token": refresh_token
        }, HTTPStatus.OK


@ns_auth.route("/register/kakao/trainer")
class TrainerKakaoAuthResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_service = TokenService()
        self.auth_service = AuthService()
        self.trainer_service = ServiceFactory.trainer_service()

    @validate()
    def post(self, body: KakaoTrainerRegisterRequest):
        trainer_social_id = self.auth_service.authenticate_kakao_user(body.kakao_token)
        trainer = self.trainer_service.get_trainer_by_social_id(trainer_social_id)
        if trainer:
            raise BadRequestError(message='이미 존재하는 트레이너입니다.')

        data = body.__dict__
        data['trainer_social_id'] = trainer_social_id
        trainer = self.trainer_service.create_trainer(data)

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

        response = {"access_token": new_access_token, "refresh_token": refresh_token}
        if new_refresh_token:
            response["refresh_token"] = new_refresh_token

        return response, HTTPStatus.OK


@ns_auth.route("/token-type-check")
class TokenTypeCheck(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user_id_key = 'user_id'
        if user_id_key in current_user:
            return {
                'user_id': current_user[user_id_key]
            }, 200

        trainer_id_key = 'trainer_id'
        if trainer_id_key in current_user:
            return {
                'trainer_id': current_user[trainer_id_key]
            }, 200

        raise UnAuthorizedError(message='유효하지 않는 토큰입니다.')


@ns_auth.route("/login/kakao/user")
class UserKakaoLogin(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_service = TokenService()
        self.auth_service = AuthService()

    @validate()
    def get(self, query: KakaoAuthRequest):
        user = self.auth_service.auth_gymming_kakao_user(query.kakao_token)

        if user is None:
            raise UnAuthorizedError(message="가입되지 않은 회원입니다.")

        identity = {"user_id": user.user_id}
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        self.token_service.insert_user_token(user.user_id, refresh_token)

        return {
            "user_id": user.user_id,
            "access_token": access_token,
            "refresh_token": refresh_token
        }, HTTPStatus.OK


@ns_auth.route("/login/kakao/trainer")
class TrainerKakaoLogin(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token_service = TokenService()
        self.auth_service = AuthService()

    @validate()
    def get(self, query: KakaoAuthRequest):
        trainer = self.auth_service.auth_gymming_kakao_trainer(query.kakao_token)

        if trainer is None:
            raise UnAuthorizedError(message="가입되지 않은 트레이너 입니다.")

        identity = {"trainer_id": trainer.trainer_id}
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)

        self.token_service.insert_trainer_token(trainer.trainer_id, refresh_token)

        return {
            "trainer_id": trainer.trainer_id,
            "access_token": access_token,
            "refresh_token": refresh_token
        }, HTTPStatus.OK
