from flask_restx import Namespace, fields, Resource, reqparse
from sqlalchemy import and_

from app.common.constants import CHANGE_FROM_USER, CHANGE_TICKET_STATUS_WAITING, CHANGE_TICKET_STATUS_REJECTED, \
    CHANGE_TICKET_TYPE_CANCEL, CHANGE_TICKET_STATUS_APPROVED, SCHEDULE_CANCELLED, CHANGE_TICKET_TYPE_MODIFY, \
    SCHEDULE_MODIFIED, \
    SCHEDULE_SCHEDULED, DATETIMEFORMAT
from app.entities.entity_change_ticket import ChangeTicket
from app.entities.entity_schedule import Schedule
from app.entities.entity_trainer import Trainer
from app.entities.entity_training_user import TrainingUser
from app.entities.entity_users import Users
from database import db

ns_change_ticket = Namespace('change-ticket', description='Change ticket related operations')

# 요청 생성 모델 정의
change_ticket_model = ns_change_ticket.model('ChangeTicketModel', {
    'schedule_id': fields.Integer(required=True, description='스케줄 ID'),
    'change_from': fields.String(required=True, description='요청자'),
    'change_type': fields.String(required=True, description='변경티켓 타입'),
    'description': fields.String(required=True, description='변경티켓 설명'),
    'request_time': fields.DateTime(required=True, description='변경 요청 시간')
})

# 변경티켓에 대한 승인 모델 정의
change_ticket_approve_model = ns_change_ticket.model("ChangeTicketApproveModel", {
    'id': fields.Integer(required=True, description='변경티켓 ID'),
    'change_type': fields.String(required=True, description='변경 타입'),
    'request_time': fields.String(description='변경 요청 시간')
})

# 변경티켓에 거절 모델 정의
change_ticket_reject_model = ns_change_ticket.model('ChangeTicketRejectModel', {
    'reject_reason': fields.String(required=True, description='변경 요청 거절 사유')
})


@ns_change_ticket.route('')
class ChangeTicketResource(Resource):
    @ns_change_ticket.expect(change_ticket_model)
    @ns_change_ticket.doc(description='유저 또는 트레이너가 스케줄 변경 요청시 변경티켓을 생성합니다.',
                          params={'schedule_id': '스케쥴 id',
                                  'change_from': 'USER or TRAINER',
                                  'change_type': 'CANCEL or MODIFY',
                                  'description': '요청 내용',
                                  'request_time': '2024-01-10 12:30:00(%Y-%m-%d %H:%M:%S)'
                                  })
    def post(self):
        data = ns_change_ticket.payload
        new_change_ticket = ChangeTicket(
            schedule_id=data['schedule_id'],
            change_from=data['change_from'],
            change_type=data['change_type'],
            description=data['description'],
            request_time=data['request_time']
        )
        db.session.add(new_change_ticket)  # 새로운 요청 객체를 데이터베이스 세션에 추가
        db.session.commit()  # 변경 사항을 데이터베이스에 커밋
        return {'message': '새로운 요청이 성공적으로 생성되었습니다.'}, 201


parser = reqparse.RequestParser()
parser.add_argument('trainer_id', type=int, required=True, help='트레이너 ID')
parser.add_argument('status', required=True, action='split',
                    help='요청 상태 ('
                         'CHANGE_TICKET_STATUS_WAITING, '
                         'CHANGE_TICKET_STATUS_APPROVED, '
                         'CHANGE_TICKET_STATUS_REJECTED'
                         ')'
                    )


@ns_change_ticket.route('/trainer')
class TrainerChangeTicketListResource(Resource):
    @ns_change_ticket.doc(description='트레이너에게 온 요청 리스트를 조회합니다.',
                          params={
                              'trainer_id': '트레이너 id',
                              'status': 'WAITING or APPROVED or REJECTED'
                          })
    def get(self):
        args = parser.parse_args()
        trainer_id = args['trainer_id']  # 쿼리 파라미터에서 트레이너 ID 추출
        status = args['status']  # 쿼리 파라미터에서 요청 상태 추출

        # 요청 상태에 따른 조건 분기
        if CHANGE_TICKET_STATUS_WAITING in status and len(status) == 1:
            status_condition = ChangeTicket.status == CHANGE_TICKET_STATUS_WAITING
        elif CHANGE_TICKET_STATUS_APPROVED in status and CHANGE_TICKET_STATUS_REJECTED in status and len(
                status) == 2:
            status_condition = ChangeTicket.status.in_([CHANGE_TICKET_STATUS_APPROVED, CHANGE_TICKET_STATUS_REJECTED])
        else:
            return {'message': 'Invalid Change ticket Status'}, 400

        results = db.session.query(Users.user_name, ChangeTicket.change_type, ChangeTicket.request_time,
                                   ChangeTicket.created_at,
                                   Schedule.schedule_start_time, ChangeTicket.id, ChangeTicket.status) \
            .join(Schedule,
                  and_(ChangeTicket.schedule_id == Schedule.schedule_id, ChangeTicket.change_from == CHANGE_FROM_USER,
                       status_condition)) \
            .join(TrainingUser, and_(Schedule.training_user_id == TrainingUser.training_user_id,
                                     TrainingUser.trainer_id == trainer_id)) \
            .join(Users, Users.user_id == TrainingUser.user_id) \
            .all()

        return [{'user_name': r[0], 'change_type': r[1],
                 'request_time': r[2].strftime(DATETIMEFORMAT) if r[2] else "",
                 'created_at': r[3].strftime(DATETIMEFORMAT),
                 'schedule_start_time': r[4].strftime(DATETIMEFORMAT),
                 'id': r[5], 'status': r[6]} for r in results]


@ns_change_ticket.route('/<int:id>/details')
class ChangeTicketDetailsResource(Resource):
    @ns_change_ticket.doc(description='한 요청에 대한 상세 조회를 합니다.',
                          params={
                              'id': '요청 id'
                          })
    def get(self, change_ticket_id):
        change_ticket = db.session.query(ChangeTicket.id, ChangeTicket.description) \
            .filter(ChangeTicket.id == change_ticket_id) \
            .first()

        if not change_ticket:
            return {'error': 'change ticket not found'}, 404

        return {"change_ticket_id": change_ticket[0], "description": change_ticket[1]}


@ns_change_ticket.route('/reject')
class ChangeTicketRejectResource(Resource):
    @ns_change_ticket.expect(change_ticket_reject_model)
    @ns_change_ticket.doc(description='요청을 거절 합니다',
                          params={
                              'id': '요청 id',
                              'reject_reason': '요청 거절 사유'
                          })
    def put(self):
        data = ns_change_ticket.payload  # 요청 본문에서 데이터 추출
        change_ticket_id = data.get('id')
        reject_reason = data.get('reject_reason')  # 거절 사유 추출

        change_ticket_record = ChangeTicket.query.filter_by(id=change_ticket_id).first()
        if not change_ticket_record:
            return {'message': '요청을 찾을 수 없습니다.'}, 404

        change_ticket_record.status = CHANGE_TICKET_STATUS_REJECTED  # 요청 상태를 '거절됨'으로 변경
        change_ticket_record.reject_reason = reject_reason  # 거절 사유를 데이터베이스에 업데이트

        db.session.commit()  # 변경 사항을 데이터베이스에 커밋
        return {'message': '요청이 성공적으로 거절되었습니다.', 'reject_reason': reject_reason}, 200


@ns_change_ticket.route('/approve')
class ChangeTicketApproveResource(Resource):
    @ns_change_ticket.expect(change_ticket_approve_model)
    @ns_change_ticket.doc(description='요청을 승인 합니다.',
                          params={
                              'id': '요청 id',
                              'change_type': 'CANCEL or MODIFY'
                          })
    def post(self):
        try:
            data = ns_change_ticket.payload
            change_type = data['change_type']
            id = data['id']

            if change_type != CHANGE_TICKET_TYPE_MODIFY and change_type != CHANGE_TICKET_TYPE_CANCEL:
                return {'message': '유효하지 않은 파라미터'}, 400

            change_ticket_record = ChangeTicket.query.filter_by(id=id).first()
            if not change_ticket_record:
                return {'message': 'Change ticket not found'}, 404

            if change_ticket_record.status != CHANGE_TICKET_STATUS_WAITING:
                return {'message': 'Invalid change ticket Status'}, 400

            change_ticket_record.status = CHANGE_TICKET_STATUS_APPROVED

            schedule_record = Schedule.query.filter_by(schedule_id=change_ticket_record.schedule_id).first()
            if not schedule_record:
                return {'message': 'Schedule not found'}, 404

            if change_type == CHANGE_TICKET_TYPE_CANCEL:
                schedule_record.schedule_status = SCHEDULE_CANCELLED

            if change_type == CHANGE_TICKET_TYPE_MODIFY:
                training_user = TrainingUser.query.filter_by(training_user_id=schedule_record.training_user_id).first()
                trainer_id = training_user.trainer_id
                request_time = change_ticket_record.request_time
                if not request_time:
                    return {'message': 'Request time of change ticket is missing'}, 400

                conflict_schedule = Trainer.conflict_trainer_schedule(trainer_id, request_time)

                if conflict_schedule:
                    # 충돌하는 스케줄이 있는 경우
                    return {'message': 'New schedule conflicts with existing schedules of the trainer'}, 400

                schedule_record.schedule_status = SCHEDULE_MODIFIED
                # todo : db.session.add(schedule_record)
                new_schedule = Schedule(
                    training_user_id=schedule_record.training_user_id,
                    schedule_start_time=request_time,
                    schedule_status=SCHEDULE_SCHEDULED
                )
                db.session.add(new_schedule)

            db.session.commit()
            return {'message': 'Update successful'}, 200

        except Exception as e:
            print(e)

# 컨트롤러의 역할 : 유효성 검사
# todo : 서비스 레이어로 비즈니스 로직 빼기.
# todo : 중앙집중식 에러 처리. 에러 헨들러 작성.
# todo : 로깅.
# todo : 환경 변수 적용
# todo : 리스트 조회시 pagenation 적용.
# todo : 시간 지난 pt 완료 처리 하는 api? batch?
