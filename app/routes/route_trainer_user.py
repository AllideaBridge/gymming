from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from app.services.service_trainer_user import trainer_user_service

ns_trainer_user = Namespace('trainer-user', description='TrainerUser API')


@ns_trainer_user.route('/trainer/<int:trainer_id>/users')
class TrainerUsers(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tu_service = trainer_user_service

    def get(self, trainer_id):
        try:
            parser = ns_trainer_user.parser()
            parser.add_argument('trainer_user_delete_flag', type=bool, help='TrainerUser Delete flag')
            args = parser.parse_args()

            self.tu_service.get_users(trainer_id, args.get('trainer_user_delete_flag'))

            return {}, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400

    def post(self, trainer_id):
        try:
            return {}, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400


@ns_trainer_user.route('/trainer/<int:trainer_id>/users/<int:user_id>')
class TrainerUser(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, trainer_id, user_id):
        try:
            return {}, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400

    def put(self, trainer_id, user_id):
        try:
            return {}, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400

    def delete(self, trainer_id, user_id):
        try:
            return {}, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400


@ns_trainer_user.route('/user/<int:user_id>/trainers')
class UserTrainers(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, user_id):
        try:
            return {}, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400
