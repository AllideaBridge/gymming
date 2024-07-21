from flask_restx import fields, Model

user_of_trainer = Model('UserOfTrainer', {
    'user_id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'user_name': fields.String(description='User name'),
    'user_profile_img_url': fields.String(description='User profile image URL'),
    'exercise_days': fields.String(description='Exercise Days'),
    'lesson_current_count': fields.Integer(description='Lesson Current Count'),
    'lesson_total_count': fields.Integer(description='Lesson Total Count'),
    'registered_date': fields.String(description='등록 날짜'),
    'last_date': fields.String(description='종료 날짜')
})

users_of_trainer = {
    'results': fields.List(fields.Nested(user_of_trainer))
}

trainer_of_user = Model('TrainerOfUser', {
    'trainer_id': fields.Integer(readOnly=True, description='The trainer unique identifier'),
    'trainer_name': fields.String(description='Trainer name'),
    'trainer_profile_img_url': fields.String(description='Trainer profile image URL'),
    'lesson_current_count': fields.Integer(description='Lesson Current Count'),
    'lesson_total_count': fields.Integer(description='Lesson Total Count'),
    'center_name': fields.String(description='센터 이름'),
    'center_location': fields.String(description='센터 위치'),
})

trainers_of_user = {
    'results': fields.List(fields.Nested(trainer_of_user))
}

user_detail_of_trainer = Model('User Details of Trainer', {
    'name': fields.String(description='User name'),
    'email': fields.String(description='User email'),
    'gender': fields.String(description='User gender'),
    'phone_number': fields.String(description='User phone number'),
    'user_profile_img_url': fields.String(description='User profile url'),
    'delete_flag': fields.Boolean(),
    'birthday': fields.String(description='User birthday'),
    'lesson_total_count': fields.Integer(description='Lesson Total Count'),
    'lesson_current_count': fields.Integer(description='Lesson Current Count'),
    'exercise_days': fields.String(description='User exercise days'),
    'special_notice': fields.String(description='User special notice'),
    'registered_date': fields.String(description='등록 날짜'),
    'last_date': fields.String(description='종료 날짜'),
})
