from flask_restx import fields, Model, SchemaModel


class CreateChangeTicketRequest(SchemaModel):
    schedule_id = fields.Integer(required=True)
    change_from = fields.String(required=True)
    change_type = fields.String(required=True)
    change_reason = fields.String(required=True)
    start_time = fields.String(required=True)

    def __init__(self, data):
        super().__init__(name='CreateChangeTicketRequest')
        self.schedule_id = data['schedule_id']
        self.change_from = data['change_from']
        self.change_type = data['change_type']
        self.change_reason = data['change_reason']
        self.start_time = data['start_time']


class UpdateChangeTicketRequest(SchemaModel):
    change_from = fields.String(required=True)
    change_type = fields.String(required=True)
    status = fields.String(required=True)
    change_reason = fields.String(required=True)
    reject_reason = fields.String(required=True)
    start_time = fields.String(required=True)

    def __init__(self, data):
        super().__init__(name='UpdateChangeTicketRequest')
        self.change_from = data['change_from']
        self.change_type = data['change_type']
        self.status = data['status']
        self.change_reason = data['change_reason']
        self.reject_reason = data['reject_reason']
        self.start_time = data['start_time']


class ChangeTicketResponse:
    change_ticket = Model('ChangeTicketList', {
        'change_from': fields.String(),
        'change_type': fields.String(),
        'created_at': fields.String(),
        'description': fields.String(),
        'id': fields.Integer(),
        'reject_reason': fields.String(),
        'request_time': fields.String(),
        'schedule_id': fields.String(),
        'status': fields.String()
    })

    trainer_receive_change_ticket_list = Model('TrainerReceiveChangeTicket', {
        'id': fields.Integer(description='Change Ticket unique identifier'),
        'user_name': fields.String(description='변경티켓을 보낸 유저 이름'),
        'change_ticket_type': fields.String(description='변경티켓 타입. '
                                                        'MODIFY: PT 날짜를 수정하고 싶은 경우'
                                                        'CANCEL: 해당 날짜의 PT를 취소하고 싶은 경우'),
        'as_is_date': fields.String(description='변경 전 날짜'),
        'to_be_date': fields.String(description='변경 희망 날짜'),
        'created_at': fields.String(description='변경티켓 생성 날짜'),
        'change_ticket_status': fields.String(description='변경 티켓 상태. '
                                                          'WAITING: 트레이너의 티켓 처리를 대기중인 상태'
                                                          'APPROVED: 트레이너가 해당 티켓을 수락한 상태'
                                                          'REJECTED: 트레이너가 해당 티켓을 거절한 상태'
                                                          'CANCELED: 유저가 해당 티켓을 취소한 상태'),
        'user_message': fields.String(description='유저의 변경 티켓에 대한 메세지.'),
        'trainer_message': fields.String(description='트레이너의 변경 티켓에 대한 메세지.')
    })

    user_receive_change_ticket_list = Model('UserReceiveChangeTicket', {
        'id': fields.Integer(description='Change Ticket unique identifier'),
        'trainer_name': fields.String(description='변경티켓을 보낸 트레이너의 이름'),
        'change_ticket_type': fields.String(description='변경티켓 타입. '
                                                        'MODIFY: PT 날짜를 수정하고 싶은 경우'
                                                        'CANCEL: 해당 날짜의 PT를 취소하고 싶은 경우'),
        'as_is_date': fields.String(description='변경 전 날짜'),
        'to_be_date': fields.String(description='변경 희망 날짜'),
        'created_at': fields.String(description='변경티켓 생성 날짜'),
        'change_ticket_status': fields.String(description='변경 티켓 상태. '
                                                          'WAITING: 트레이너의 티켓 처리를 대기중인 상태'
                                                          'APPROVED: 트레이너가 해당 티켓을 수락한 상태'
                                                          'REJECTED: 트레이너가 해당 티켓을 거절한 상태'
                                                          'CANCELED: 유저가 해당 티켓을 취소한 상태'),
        'user_message': fields.String(description='유저의 변경 티켓에 대한 메세지.'),
        'trainer_message': fields.String(description='트레이너의 변경 티켓에 대한 메세지.')
    })

    user_send_change_ticket_list = Model('UserSendChangeTicket', {
        'id': fields.Integer(description='Change Ticket unique identifier'),
        'trainer_name': fields.String(description='변경 티켓을 받을 트레이너 이름'),
        'change_ticket_type': fields.String(description='변경티켓 타입. '
                                                        'MODIFY: PT 날짜를 수정하고 싶은 경우'
                                                        'CANCEL: 해당 날짜의 PT를 취소하고 싶은 경우'),
        'as_is_date': fields.String(description='변경 전 날짜'),
        'to_be_date': fields.String(description='변경 희망 날짜'),
        'created_at': fields.String(description='변경티켓 생성 날짜'),
        'change_ticket_status': fields.String(description='변경 티켓 상태. '
                                                          'WAITING: 트레이너의 티켓 처리를 대기중인 상태'
                                                          'APPROVED: 트레이너가 해당 티켓을 수락한 상태'
                                                          'REJECTED: 트레이너가 해당 티켓을 거절한 상태'
                                                          'CANCELED: 유저가 해당 티켓을 취소한 상태'),
        'user_message': fields.String(description='유저의 변경 티켓에 대한 메세지.'),
        'trainer_message': fields.String(description='트레이너의 변경 티켓에 대한 메세지.')
    })
