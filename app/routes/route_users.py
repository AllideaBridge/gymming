from datetime import datetime
from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields

from app.common.constants import DATEFORMAT
from app.common.exceptions import BadRequestError, UnAuthorizedError
from app.services.service_user import user_service

ns_user = Namespace('users', description='User API')

user_model = ns_user.model('Users', {
    'user_id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'user_email': fields.String(description='User email address'),
    'user_name': fields.String(description='User name'),
    'user_gender': fields.String(description='User gender'),
    'user_phone_number': fields.String(description='User phone number'),
    'user_profile_img_url': fields.String(description='User profile image URL'),
    'user_delete_flag': fields.Boolean(default=False, description='User delete flag'),
    'user_birthday': fields.String(description='User BirthDay')
})


@ns_user.route('/<int:user_id>')
class UserResource(Resource):
    @ns_user.marshal_with(user_model)
    @jwt_required()
    def get(self, user_id):
        current_user = get_jwt_identity()

        if user_id != current_user['user_id']:
            raise UnAuthorizedError(message="유효하지 않는 id입니다.")

        return user_service.get_user(user_id)

    @ns_user.expect(user_model)
    @ns_user.marshal_with(user_model)
    @jwt_required()
    def put(self, user_id):
        current_user = get_jwt_identity()

        if user_id != current_user['user_id']:
            raise UnAuthorizedError(message="유효하지 않는 id입니다.")

        user = user_service.get_user(user_id)
        if user is None:
            raise BadRequestError(message="존재하지 않는 유저입니다.")

        update_data = ns_user.payload

        if update_data.get('user_birthday') is not None:
            update_data['user_birthday'] = datetime.strptime(update_data['user_birthday'], DATEFORMAT).date()

        updated_user = user_service.update_user(user, update_data)
        return updated_user


@ns_user.route('')
class UserListResource(Resource):
    @ns_user.expect(user_model, validate=True)
    @ns_user.marshal_with(user_model, code=201)
    def post(self):
        new_user = user_service.create_user(ns_user.payload)
        return new_user, 201


@ns_user.route('/check')
class UserCheck(Resource):

    def get(self):
        user_name = request.args.get('user_name')
        user_phone_number = request.args.get('user_phone_number')

        if not user_name or not user_phone_number:
            raise BadRequestError("Both user_name and user_phone_number are required")

        result = user_service.check_user_exists(user_name, user_phone_number)
        return result
