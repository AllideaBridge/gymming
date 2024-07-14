from flask_restx import fields, Model

user_show_response = Model('Users', {
    'user_id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'user_email': fields.String(description='User email address'),
    'user_name': fields.String(description='User name'),
    'user_gender': fields.String(description='User gender'),
    'user_phone_number': fields.String(description='User phone number'),
    'user_profile_img_url': fields.String(description='User profile image URL'),
    'user_delete_flag': fields.Boolean(default=False, description='User delete flag'),
    'user_birthday': fields.String(description='User BirthDay')
})