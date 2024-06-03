from flask_restx import Namespace, Resource
from marshmallow import ValidationError

from app.common.constants import CHANGE_TICKET_TYPE_CANCEL, CHANGE_TICKET_TYPE_MODIFY
from app.common.exceptions import ApplicationError
from app.routes.models.model_change_ticket import CreateChangeTicketRequest, UpdateChangeTicketRequest
from app.services.service_change_ticket import ChangeTicketService

ns_change_ticket = Namespace('change-ticket', description='Change ticket related operations')


@ns_change_ticket.route('')
class ChangeTicket(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_ticket_service = ChangeTicketService()

    def post(self):
        try:
            body = CreateChangeTicketRequest(ns_change_ticket.payload)
            self.change_ticket_service.create_change_ticket(body)
            return {'message': '새 변경 요청이 대기 상태로 생성되었습니다.'}, 200
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400


@ns_change_ticket.route('/<int:change_ticket_id>')
class ChangeTicketWithID(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.change_ticket_service = ChangeTicketService()

    def get(self, change_ticket_id):
        try:
            change_ticket = self.change_ticket_service.get_change_ticket_by_id(change_ticket_id)
            return jsonify(change_ticket.to_dict())
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400

    def put(self, change_ticket_id):
        try:
            body = UpdateChangeTicketRequest(ns_change_ticket.payload)

            self.change_ticket_service.handle_update_change_ticket(change_ticket_id, body)

            return {'message': '변경 티켓을 수정했습니다.'}, 200
        except ApplicationError as e:
            return {'message': e.message}, 400
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400

    def delete(self, change_ticket_id):
        try:
            self.change_ticket_service.delete_change_ticket(change_ticket_id)
            return {'message': '변경 티켓을 삭제했습니다.'}, 200
        except ApplicationError as e:
            return {'message': e.message}, 400
        except ValidationError as e:
            return {'message': '입력 데이터가 올바르지 않습니다.', 'errors': e.messages}, 400


@ns_change_ticket.route('/trainer/<int:id>')
class ChangeTicketTrainer(Resource):
    def get(self, status, page):
        return {'message': '아직 개발중인 API'}, 500


@ns_change_ticket.route('/user/<int:id>')
class ChangeTicketUser(Resource):
    def get(self, status, page):
        return {'message': '아직 개발중인 API'}, 500

# 컨트롤러의 역할 : 유효성 검사
# todo : 서비스 레이어로 비즈니스 로직 빼기.
# todo : 중앙집중식 에러 처리. 에러 헨들러 작성.
# todo : 로깅.
# todo : 환경 변수 적용
# todo : 리스트 조회시 pagenation 적용.
# todo : 시간 지난 pt 완료 처리 하는 api? batch?
