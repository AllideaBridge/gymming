from flask_restx import fields

request_get_schedules_model = {
    'training_user_id': fields.Integer,
    'trainer_id': fields.Integer,
    'user_id': fields.Integer,
    'year': fields.Integer,
    'month': fields.Integer,
    'day': fields.Integer,
    'week': fields.Boolean,
    'possible': fields.Boolean,
    'page': fields.Integer,
    'per_page': fields.Integer
}
