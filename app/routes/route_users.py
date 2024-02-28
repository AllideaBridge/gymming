from flask_restx import Namespace, Resource, fields

from app.models.model_Users import Users
from database import db

ns_user = Namespace('users', description='User API')

user_model = ns_user.model('Users', {
    'user_id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'user_email': fields.String(required=True, description='User email address'),
    'user_name': fields.String(description='User name'),
    'user_gender': fields.String(description='User gender'),
    'user_phone_number': fields.String(description='User phone number'),
    'user_profile_img_url': fields.String(description='User profile image URL'),
    'user_delete_flag': fields.Boolean(default=False, description='User delete flag'),
    'user_login_platform': fields.String(required=True, description='User login platform')
})


@ns_user.route('/<int:user_id>')
class UserResource(Resource):
    @ns_user.marshal_with(user_model)
    def get(self, user_id):
        user = Users.query.get_or_404(user_id)
        # todo : filter_by 로 수정
        return user

    @ns_user.expect(user_model)
    @ns_user.marshal_with(user_model)
    def put(self, user_id):
        user = Users.query.get_or_404(user_id)
        # todo : filter_by 로 수정 후 없는 경우 예외처리
        data = ns_user.payload

        user.user_email = data.get('user_email', user.user_email)
        user.user_name = data.get('user_name', user.user_name)
        user.user_gender = data.get('user_gender', user.user_gender)
        user.user_phone_number = data.get('user_phone_number', user.user_phone_number)
        user.user_profile_img_url = data.get('user_profile_img_url', user.user_profile_img_url)
        user.user_delete_flag = data.get('user_delete_flag', user.user_delete_flag)
        user.user_login_platform = data.get('user_login_platform', user.user_login_platform)

        db.session.commit()
        return user


@ns_user.route('')
class UserListResource(Resource):
    @ns_user.expect(user_model, validate=True)
    @ns_user.marshal_with(user_model, code=201)
    def post(self):
        data = ns_user.payload
        user = Users(
            user_email=data['user_email'],
            user_name=data.get('user_name'),
            user_gender=data.get('user_gender'),
            user_phone_number=data.get('user_phone_number'),
            user_profile_img_url=data.get('user_profile_img_url'),
            user_delete_flag=data.get('user_delete_flag', False),
            user_login_platform=data['user_login_platform']
        )
        db.session.add(user)
        db.session.commit()
        return user, 201
