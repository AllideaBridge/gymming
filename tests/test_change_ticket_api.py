from datetime import datetime

from app.common.constants import const
from app.entities.entity_change_ticket import ChangeTicket
from app.entities.entity_schedule import Schedule
from app.entities.entity_trainer_user import TrainerUser
from database import db
from tests import BaseTestCase
from tests.test_data_factory import TestDataFactory, ChangeTicketBuilder


class TestChangeTicketApi(BaseTestCase):
    def test_유저_티켓생성(self):
        user = TestDataFactory.create_user()
        schedule = TestDataFactory.create_schedule()

        body = {
            "schedule_id": schedule.schedule_id,
            "change_from": "USER",
            "change_type": "CANCEL",
            "change_reason": "그냥",
            "start_time": "2024-05-13T12:00:00"
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.post(f'/change-ticket', headers=headers, json=body)

        self.assertEqual(response.status_code, 200)


class TrainerScheduleTestCase(BaseTestCase):
    def test_트레이너_변경티켓_대기_리스트_조회(self):
        trainer = TestDataFactory.create_trainer()
        waiting_tickets = [
            ChangeTicketBuilder()
            .with_trainer(trainer)
            .with_status(const.CHANGE_TICKET_STATUS_WAITING)
            .build()
            for _ in range(3)
        ]
        # 다른 상태의 티켓도 생성
        ChangeTicketBuilder().with_trainer(trainer).with_status(const.CHANGE_TICKET_STATUS_APPROVED).build()

        # 다른 트레이너의 대기 티켓 생성 (이 티켓은 결과에 포함되면 안 됨)
        other_trainer = TestDataFactory.create_trainer()
        ChangeTicketBuilder().with_trainer(other_trainer).with_status(const.CHANGE_TICKET_STATUS_WAITING).build()

        headers = TestDataFactory.create_trainer_auth_header(trainer.trainer_id)
        response = self.client.get(
            f'/change-ticket/trainer/{trainer.trainer_id}?status={const.CHANGE_TICKET_STATUS_WAITING}',
            headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(len(data), len(waiting_tickets))

        for req in data:
            self.assertEqual(req['change_ticket_status'], const.CHANGE_TICKET_STATUS_WAITING)

        # 데이터베이스에서 직접 확인
        db_tickets = db.session.query(ChangeTicket).join(Schedule).join(TrainerUser).filter(
            TrainerUser.trainer_id == trainer.trainer_id,
            ChangeTicket.status == const.CHANGE_TICKET_STATUS_WAITING
        ).all()

        self.assertEqual(len(db_tickets), len(data), "데이터베이스의 티켓 수와 응답의 티켓 수가 일치해야 합니다.")

        for db_ticket in db_tickets:
            self.assertTrue(any(ticket['id'] == db_ticket.id for ticket in data),
                            f"데이터베이스의 티켓 ID {db_ticket.id}가 응답에 포함되어야 합니다.")

    def test_트레이너_변경티켓_완료_리스트_조회(self):
        trainer = TestDataFactory.create_trainer()

        for _ in range(3):
            ChangeTicketBuilder() \
                .with_trainer(trainer) \
                .with_status(const.CHANGE_TICKET_STATUS_WAITING) \
                .build()
        for _ in range(3):
            ChangeTicketBuilder() \
                .with_trainer(trainer) \
                .with_status(const.CHANGE_TICKET_STATUS_REJECTED) \
                .build()
        for _ in range(3):
            ChangeTicketBuilder() \
                .with_trainer(trainer) \
                .with_status(const.CHANGE_TICKET_STATUS_APPROVED) \
                .build()

        headers = TestDataFactory.create_trainer_auth_header(trainer.trainer_id)
        response = self.client.get(
            f'/change-ticket/trainer/{trainer.trainer_id}?'
            f'status={const.CHANGE_TICKET_STATUS_APPROVED},{const.CHANGE_TICKET_STATUS_REJECTED}',
            headers=headers
        )
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 6)

        if data:
            for req in data:
                r = db.session.query(TrainerUser.trainer_id, ChangeTicket.status) \
                    .join(Schedule, ChangeTicket.schedule_id == Schedule.schedule_id) \
                    .join(TrainerUser, Schedule.trainer_user_id == TrainerUser.trainer_user_id) \
                    .filter(ChangeTicket.id == req['id']) \
                    .first()
                self.assertEqual(r[0], trainer.trainer_id)
                self.assertIn(r[1], [const.CHANGE_TICKET_STATUS_APPROVED, const.CHANGE_TICKET_STATUS_REJECTED])

    def test_유효하지_않은_파라미터로_트레이너_변경티켓_리스트_조회(self):
        non_exist_trainer_id = 111
        headers = TestDataFactory.create_trainer_auth_header(non_exist_trainer_id)
        response = self.client.get(
            f'/change-ticket/trainer/{non_exist_trainer_id}?'
            f'status={const.CHANGE_TICKET_STATUS_WAITING},{const.CHANGE_TICKET_STATUS_REJECTED}',
            headers=headers
        )

        self.assertEqual(400, response.status_code)

    def test_변경티켓_상세조회(self):
        user = TestDataFactory.create_user()
        change_ticket = TestDataFactory.create_change_ticket()

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.get(f'/change-ticket/{change_ticket.id}', headers=headers)
        data = response.get_json()

        self.assertEqual(data['id'], change_ticket.id)
        self.assertIn('description', data, msg='description is missing in response')

    def test_없는_변경티켓_상세조회(self):
        user = TestDataFactory.create_user()
        change_ticket_id = 111

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.get(f'/change-ticket/{change_ticket_id}', headers=headers)

        self.assertEqual(response.status_code, 400)

    def test_유저의_요청_거절(self):
        user = TestDataFactory.create_user()
        change_ticket = TestDataFactory.create_change_ticket(status=const.CHANGE_TICKET_STATUS_WAITING)
        reject_reason = "I'm busy too."
        body = {
            "change_from": "USER",
            "change_type": const.CHANGE_TICKET_TYPE_MODIFY,
            "status": const.CHANGE_TICKET_STATUS_REJECTED,
            "change_reason": "I go travel.",
            "reject_reason": reject_reason,
            "start_time": "2024-05-26T12:00:00"
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        self.client.put(f'/change-ticket/{change_ticket.id}', headers=headers, json=body)

        data: ChangeTicket = ChangeTicket.query.filter_by(id=change_ticket.id).first()
        self.assertEqual(change_ticket.id, data.id)
        self.assertEqual(const.CHANGE_TICKET_STATUS_REJECTED, data.status)
        self.assertEqual(reject_reason, data.reject_reason)

    def test_유효하지_않은_change_type으로_Change_ticket_생성한_경우(self):
        user = TestDataFactory.create_user()
        schedule = TestDataFactory.create_schedule()

        body = {
            "schedule_id": schedule.schedule_id,
            "change_from": const.CHANGE_FROM_USER,
            "change_type": "INVALID_CHANGE_TYPE",
            "change_reason": "그냥",
            "start_time": "2024-05-13T12:00:00"
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.post(f'/change-ticket', headers=headers, json=body)
        self.assertEqual(response.status_code, 400)

    def test_취소변경티켓이_승인된_경우(self):
        user = TestDataFactory.create_user()
        schedule = TestDataFactory.create_schedule()
        cancel_change_ticket = TestDataFactory.create_change_ticket(
            schedule=schedule,
            status=const.CHANGE_TICKET_STATUS_WAITING,
            change_type=const.CHANGE_TICKET_TYPE_CANCEL
        )

        body = {
            "change_from": "USER",
            "change_type": const.CHANGE_TICKET_TYPE_CANCEL,
            "status": const.CHANGE_TICKET_STATUS_APPROVED,
            "change_reason": "I go travel.",
            "reject_reason": "",
            "start_time": "2024-05-26T12:00:00"
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.put(f'/change-ticket/{cancel_change_ticket.id}', headers=headers, json=body)

        change_ticket = ChangeTicket.query.filter_by(id=cancel_change_ticket.id).first()
        schedule = Schedule.query.filter_by(schedule_id=schedule.schedule_id).first()
        self.assertEqual(200, response.status_code)
        self.assertEqual(const.CHANGE_TICKET_STATUS_APPROVED, change_ticket.status)
        self.assertEqual(const.SCHEDULE_CANCELLED, schedule.schedule_status)

    def test_시간변경티켓이_승인된_경우(self):
        user = TestDataFactory.create_user()
        schedule = TestDataFactory.create_schedule()
        change_ticket = TestDataFactory.create_change_ticket(
            schedule=schedule,
            change_type=const.CHANGE_TICKET_TYPE_MODIFY,
            status=const.CHANGE_TICKET_STATUS_WAITING,
        )

        start_time = datetime.now().strftime(const.DATETIMEFORMAT)
        body = {
            "change_from": "USER",
            "change_type": const.CHANGE_TICKET_TYPE_MODIFY,
            "status": const.CHANGE_TICKET_STATUS_APPROVED,
            "change_reason": "I go travel.",
            "reject_reason": "",
            "start_time": start_time
        }
        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.put(f'/change-ticket/{change_ticket.id}', headers=headers, json=body)

        change_ticket = ChangeTicket.query.filter_by(id=change_ticket.id).first()
        schedule = Schedule.query.filter_by(schedule_id=schedule.schedule_id).first()
        new_schedule = Schedule.query.filter_by(trainer_user_id=schedule.trainer_user_id,
                                                schedule_start_time=start_time).first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(change_ticket.status, const.CHANGE_TICKET_STATUS_APPROVED)
        self.assertEqual(schedule.schedule_status, const.SCHEDULE_MODIFIED)
        self.assertEqual(schedule.schedule_id, new_schedule.schedule_id)
        self.assertIsNotNone(new_schedule)

    def test_변경티켓_상태가_WAITING이_아닐때_수정할_경우(self):
        user = TestDataFactory.create_user()
        change_ticket = TestDataFactory.create_change_ticket(
            status=const.CHANGE_TICKET_STATUS_REJECTED
        )

        body = {
            "change_from": "USER",
            "change_type": const.CHANGE_TICKET_TYPE_MODIFY,
            "status": const.CHANGE_TICKET_STATUS_APPROVED,
            "change_reason": "I go travel.",
            "reject_reason": "",
            "start_time": datetime.now().strftime(const.DATETIMEFORMAT)
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.put(f'/change-ticket/{change_ticket.id}', headers=headers, json=body)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], f'이미 처리된 Change Ticket 입니다. {change_ticket.id}')

    def test_변경티켓_시간에_이미_스케쥴이_있는데_수락하는_경우(self):
        # Given
        user = TestDataFactory.create_user()
        trainer = TestDataFactory.create_trainer()
        trainer_user = TestDataFactory.create_trainer_user(trainer=trainer, user=user)

        already_exist_time = "2024-07-29 18:00:00"
        already_exist_schedule = TestDataFactory.create_schedule(
            trainer_user=trainer_user,
            start_time=already_exist_time,
            schedule_status=const.SCHEDULE_SCHEDULED
        )
        change_ticket = TestDataFactory.create_change_ticket(
            schedule=already_exist_schedule,
            change_type=const.CHANGE_TICKET_TYPE_MODIFY,
            change_from=const.CHANGE_FROM_USER,
            status=const.CHANGE_TICKET_STATUS_WAITING
        )

        # When
        body = {
            "change_from": "USER",
            "change_type": const.CHANGE_TICKET_TYPE_MODIFY,
            "status": const.CHANGE_TICKET_STATUS_APPROVED,
            "change_reason": "I go travel.",
            "reject_reason": "",
            "start_time": "2024-07-29 18:30:00"
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.put(f'/change-ticket/{change_ticket.id}', headers=headers, json=body)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'],
                         'New schedule conflicts with existing schedules of the trainer')

    def test_get_change_ticket_history(self):
        user = TestDataFactory.create_user()
        size = 2
        for _ in range(size):
            ChangeTicketBuilder().with_user(user).with_change_from(const.CHANGE_FROM_USER).build()

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.get(f'/change-ticket/user/{user.user_id}/history', headers=headers)
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), size)
        print(data)
