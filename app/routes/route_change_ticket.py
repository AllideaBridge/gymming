from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from app.common.constants import const
from app.common.exceptions import ApplicationError, UnAuthorizedError, BadRequestError
from app.models.model_change_ticket import ChangeTicketResponse
from app.models.model_change_ticket import CreateChangeTicketRequest, UpdateChangeTicketRequest
from app.services.service_factory import ServiceFactory

ns_change_ticket = Namespace('change-ticket', description='Change ticket related operations')


@ns_change_ticket.route('')
class ChangeTicket(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_ticket_service = ServiceFactory.change_ticket_service()

    @jwt_required()
    @validate()
    def post(self, body: CreateChangeTicketRequest):
        try:
            current_auth: dict = get_jwt_identity()

            if body.change_from == const.CHANGE_FROM_USER:
                if 'user_id' not in current_auth:
                    raise UnAuthorizedError(message="유효하지 않는 id입니다.")
            elif body.change_from == const.CHANGE_FROM_TRAINER:
                if 'trainer_id' not in current_auth:
                    raise UnAuthorizedError(message="유효하지 않는 id 입니다.")

            if body.change_type not in [const.CHANGE_TICKET_TYPE_MODIFY,
                                        const.CHANGE_TICKET_TYPE_CANCEL]:
                raise ValidationError(message=f"change_type can be {const.CHANGE_TICKET_TYPE_CANCEL} "
                                              f"or {const.CHANGE_TICKET_TYPE_MODIFY}")
            change_ticket = self.change_ticket_service.create_change_ticket(body)
            return {
                'change_ticket_id': change_ticket.id,
                'message': '새 변경 요청이 대기 상태로 생성되었습니다.'
            }, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400


@ns_change_ticket.route('/<int:change_ticket_id>')
class ChangeTicketWithID(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_ticket_service = ServiceFactory.change_ticket_service()

    # 해당 api는 사용하지 않고, 리스트 조회에서 받은 값으로 대체 가능.
    @ns_change_ticket.marshal_with(ChangeTicketResponse.change_ticket)
    @jwt_required()
    def get(self, change_ticket_id):
        try:
            current_auth = get_jwt_identity()
            if 'user_id' not in current_auth and 'trainer_id' not in current_auth:
                raise UnAuthorizedError(message="유효하지 않는 id입니다.")

            change_ticket = self.change_ticket_service.get_change_ticket_by_id(change_ticket_id)
            return change_ticket
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400
        except UnAuthorizedError as e:
            return {'message': e.message}, 400
        except BadRequestError as e:
            return {'message': e.message}, 400

    @jwt_required()
    @validate()
    def put(self, change_ticket_id, body: UpdateChangeTicketRequest):
        try:
            self.change_ticket_service.handle_update_change_ticket(change_ticket_id, body)

            return {'message': '변경 티켓을 수정했습니다.'}, 200
        except ApplicationError as e:
            return {'message': e.message}, 400
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400

    @jwt_required()
    def delete(self, change_ticket_id):
        try:
            self.change_ticket_service.delete_change_ticket(change_ticket_id)
            return {'message': '변경 티켓을 삭제했습니다.'}, 200
        except ApplicationError as e:
            return {'message': e.message}, 400
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400


@ns_change_ticket.route('/trainer/<int:trainer_id>')
class ChangeTicketTrainer(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_ticket_service = ServiceFactory.change_ticket_service()

    @ns_change_ticket.marshal_list_with(ChangeTicketResponse.trainer_receive_change_ticket_list)
    @jwt_required()
    def get(self, trainer_id):
        try:
            current_trainer = get_jwt_identity()
            if trainer_id != current_trainer['trainer_id']:
                raise UnAuthorizedError(message="유효하지 않는 id입니다.")

            parser = ns_change_ticket.parser()
            parser.add_argument('status', type=str, help='Status of the item')
            parser.add_argument('page', type=int, help='Page number of the item')
            args = parser.parse_args()

            change_ticket_list = []
            for status in args.get('status').split(','):
                result = self.change_ticket_service.get_change_ticket_list_by_trainer(
                    trainer_id, status, args.get('page')
                )
                change_ticket_list.extend(result)
            return change_ticket_list
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400
        except BadRequestError as e:
            return {'message': e.message}, 400
        except UnAuthorizedError as e:
            return {'message': e.message}, 400


@ns_change_ticket.route('/user/<int:user_id>')
class ChangeTicketUser(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_ticket_service = ServiceFactory.change_ticket_service()

    @ns_change_ticket.marshal_list_with(ChangeTicketResponse.user_receive_change_ticket_list)
    @jwt_required()
    def get(self, user_id):
        try:
            parser = ns_change_ticket.parser()
            parser.add_argument('status', type=str, help='Status of the item')
            parser.add_argument('page', type=int, help='Page number of the item')
            args = parser.parse_args()

            change_ticket_list = self.change_ticket_service.get_change_ticket_list_by_user(
                user_id, args.get('status'), args.get('page')
            )
            return change_ticket_list
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400


@ns_change_ticket.route('/user/<int:user_id>/history')
class UserChangeTicketHistory(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_ticket_service = ServiceFactory.change_ticket_service()

    @ns_change_ticket.marshal_list_with(ChangeTicketResponse.user_send_change_ticket_list)
    @jwt_required()
    def get(self, user_id):
        page = request.args.get('page')
        result = self.change_ticket_service.get_user_change_ticket_history(user_id, page)
        return result

# 컨트롤러의 역할 : 유효성 검사
# todo.txt : 중앙집중식 에러 처리. 에러 헨들러 작성.
# todo.txt : 로깅.
# todo.txt : 환경 변수 적용
# todo.txt : 리스트 조회시 pagenation 적용.
# todo.txt : 시간 지난 pt 완료 처리 하는 api? batch?
