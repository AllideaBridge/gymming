from flask_restx import fields, Model


trainer_availability_model = Model('Trainer_availability', {
    'trainer_availability_id': fields.Integer(),
    'trainer_id': fields.Integer(),
    'week_day': fields.String(),
    'start_time': fields.String(),
    'end_time': fields.String(),
    'possible_lesson_cnt': fields.Integer()
})

trainer_show_model = Model('Trainer', {
    'trainer_id': fields.Integer(description='Trainer ID'),
    'trainer_name': fields.String(description='Trainer Name'),
    'trainer_phone_number': fields.String(description='Trainer Phone Number'),
    'trainer_gender': fields.String(description='trainer_gender'),
    'trainer_birthday': fields.String(description='trainer_birthday'),
    'description': fields.String(description='description'),
    'lesson_name': fields.String(description='lesson_name'),
    'lesson_price': fields.Integer(description='lesson_price'),
    'lesson_minutes': fields.Integer(description='lesson_minutes'),
    'lesson_change_range': fields.Integer(description='lesson_change_range'),
    'trainer_email': fields.String(description='trainer_email'),
    'trainer_delete_flag': fields.Boolean(default=False, description='trainer_delete_flag'),
    'center_name': fields.String(description='center_name'),
    'center_location': fields.String(description='center_location'),
    'center_number': fields.String(description='center_number'),
    'center_type': fields.String(description='center_type'),
    'trainer_profile_img_url': fields.String(description='trainer_profile_img_url'),
    'trainer_availability': fields.Nested(trainer_availability_model)
})
