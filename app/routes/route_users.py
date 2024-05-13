from flask_restx import Namespace, Resource, fields

from app.services.service_user import user_service

ns_user = Namespace('users', description='User API')

user_model = ns_user.model('Users', {
    'user_id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'user_email': fields.String(required=True, description='User email address'),
    'user_name': fields.String(description='User name'),
    'user_gender': fields.String(description='User gender'),
    'user_phone_number': fields.String(description='User phone number'),
    'user_profile_img_url': fields.String(description='User profile image URL'),
    'user_delete_flag': fields.Boolean(default=False, description='User delete flag'),
    'user_birthday': fields.String(required=True, description='User BirthDay')
})


@ns_user.route('/<int:user_id>')
class UserResource(Resource):
    @ns_user.marshal_with(user_model)
    def get(self, user_id):
        return user_service.get_user(user_id)

    @ns_user.expect(user_model)
    @ns_user.marshal_with(user_model)
    def put(self, user_id):
        user = user_service.get_user(user_id)
        if user is None:
            # TODO: Exception 만들기
            raise Exception("없는 유저임")

        update_data = ns_user.payload
        updated_user = user_service.update_user(user, update_data)
        return updated_user


@ns_user.route('')
class UserListResource(Resource):
    @ns_user.expect(user_model, validate=True)
    @ns_user.marshal_with(user_model, code=201)
    def post(self):
        new_user = user_service.create_user(ns_user.payload)
        return new_user, 201
