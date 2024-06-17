from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from app.common.exceptions import BadRequestError
from app.routes.models.model_trainer_user import CreateTrainerUserRelationRequest
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
            parser.add_argument('trainer_user_delete_flag', type=str, help='TrainerUser Delete flag')
            args = parser.parse_args()
            delete_flag = True if args.get('trainer_user_delete_flag') == 'True' else False

            results = self.tu_service.get_users_related_trainer(trainer_id, delete_flag)

            return {"results": results}, 200
        except BadRequestError or ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400

    def post(self, trainer_id):
        try:
            body = CreateTrainerUserRelationRequest(ns_trainer_user.payload)
            self.tu_service.create_trainer_user_relation(trainer_id, body)
            return {'message': '새로운 회원이 등록됐습니다.'}, 200
        except BadRequestError or ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.message}, 400


@ns_trainer_user.route('/trainer/<int:trainer_id>/users/<int:user_id>')
class TrainerUser(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tu_service = trainer_user_service

    def get(self, trainer_id, user_id):
        try:
            user_detail: dict = self.tu_service.get_user_detail_related_trainer(trainer_id, user_id)
            return user_detail, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400

    def put(self, trainer_id, user_id):
        try:
            return {}, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400

    def delete(self, trainer_id, user_id):
        try:
            self.tu_service.delete_trainer_user(trainer_id, user_id)
            return {'message': '회원정보가 수정됐습니다.'}, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400


@ns_trainer_user.route('/user/<int:user_id>/trainers')
class UserTrainers(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tu_service = trainer_user_service

    def get(self, user_id):
        try:
            results = self.tu_service.get_trainers_related_user(user_id)
            return {'result': results}, 200
        except BadRequestError or ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400
