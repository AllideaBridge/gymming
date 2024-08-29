from datetime import datetime, timedelta
from unittest.mock import patch

from app.common.constants import const, CHANGE_TICKET_STATUS_APPROVED
from app.entities.entity_change_ticket import ChangeTicket
from app.entities.entity_schedule import Schedule
from app.entities.entity_trainer_user import TrainerUser
from database import db
from tests import BaseTestCase
from tests.test_data_factory import TestDataFactory, ChangeTicketBuilder, ScheduleBuilder


class TestChangeTicketApi(BaseTestCase):
    def test_변경티켓_단건조회(self):
        user = TestDataFactory.create_user()
        TestDataFactory.create_change_ticket(
            change_from=const.CHANGE_FROM_USER,
            change_type=const.CHANGE_TICKET_TYPE_MODIFY
        )

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.get(f'/change-ticket/1', headers=headers)

        result = response.get_json()
        self.assertEqual(1, result['id'])


    @patch('app.services.service_fcm.FcmService.send_message')
    def test_유저_변경_티켓_생성(self, mock_send_message):
        user = TestDataFactory.create_user()
        trainer = TestDataFactory.create_trainer()
        trainer_fcm_token = TestDataFactory.create_trainer_fcm_token(trainer)
        schedule = ScheduleBuilder().with_user(user).with_trainer(trainer).build()

        body = {
            "schedule_id": schedule.schedule_id,
            "change_from": const.CHANGE_FROM_USER,
            "change_type": const.CHANGE_TICKET_TYPE_MODIFY,
            "change_reason": "그냥",
            "start_time": "2024-05-13T12:00:00",
            "as_is_date": "2024-05-12T12:00:00"
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.post(f'/change-ticket', headers=headers, json=body)

        self.assertEqual(response.status_code, 200)

        change_ticket_id = response.get_json()['change_ticket_id']
        change_ticket_from_db = ChangeTicket.query.get(change_ticket_id)

        mock_send_message.assert_called_once_with(
            title='변경 신청',
            body=f'{user.user_name}님이 수업 변경 신청을 하였습니다.',
            token=trainer_fcm_token.fcm_token,  # 정확한 토큰 값을 확인하세요
            data={'change_ticket': change_ticket_from_db}
        )

    @patch('app.services.service_fcm.FcmService.send_message')
    def test_유저_취소_티켓_생성(self, mock_send_message):
        user = TestDataFactory.create_user()
        trainer = TestDataFactory.create_trainer()
        trainer_fcm_token = TestDataFactory.create_trainer_fcm_token(trainer)
        schedule = ScheduleBuilder().with_user(user).with_trainer(trainer).build()

        body = {
            "schedule_id": schedule.schedule_id,
            "change_from": const.CHANGE_FROM_USER,
            "change_type": const.CHANGE_TICKET_TYPE_CANCEL,
            "change_reason": "그냥",
            "as_is_date": "2024-05-12T12:00:00"
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.post(f'/change-ticket', headers=headers, json=body)

        self.assertEqual(response.status_code, 200)

        change_ticket_id = response.get_json()['change_ticket_id']
        change_ticket_from_db = ChangeTicket.query.get(change_ticket_id)

        mock_send_message.assert_called_once_with(
            title='취소 신청',
            body=f'{user.user_name}님이 수업 취소 신청을 하였습니다.',
            token=trainer_fcm_token.fcm_token,  # 정확한 토큰 값을 확인하세요
            data={'change_ticket': change_ticket_from_db}
        )

    def test_이미_티켓이_있는_경우_티켓_생성을_하면_400을_응답한다(self):
        user = TestDataFactory.create_user()
        schedule = ScheduleBuilder().with_user(user).build()
        ChangeTicketBuilder().with_schedule(schedule).build()

        body = {
            "schedule_id": schedule.schedule_id,
            "change_from": "USER",
            "change_type": "CANCEL",
            "change_reason": "그냥",
            "start_time": "2024-05-13T12:00:00",
            "as_is_date": "2024-05-12T12:00:00"
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.post(f'/change-ticket', headers=headers, json=body)
        print(response.get_json())
        self.assertEqual(response.status_code, 400)

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
        print(data)

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

    @patch('app.services.service_fcm.FcmService.send_message')
    def test_유저의_요청이_거절되는_경우(self, mock_send_message):
        user = TestDataFactory.create_user()
        user_fcm_token = TestDataFactory.create_user_fcm_token(user)
        trainer = TestDataFactory.create_trainer()
        change_ticket = (ChangeTicketBuilder()
                         .with_user(user)
                         .with_trainer(trainer)
                         .with_status(const.CHANGE_TICKET_STATUS_WAITING)
                         .build())

        reject_reason = "I'm busy too."
        body = {
            "change_from": const.CHANGE_FROM_USER,
            "change_type": const.CHANGE_TICKET_TYPE_MODIFY,
            "status": const.CHANGE_TICKET_STATUS_REJECTED,
            "change_reason": "I go travel.",
            "reject_reason": reject_reason,
            "start_time": "2024-05-26T12:00:00"
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        self.client.put(f'/change-ticket/{change_ticket.id}', headers=headers, json=body)

        data: ChangeTicket = ChangeTicket.query.get(change_ticket.id)
        self.assertEqual(change_ticket.id, data.id)
        self.assertEqual(const.CHANGE_TICKET_STATUS_REJECTED, data.status)
        self.assertEqual(reject_reason, data.reject_reason)

        # 푸시 알람이 올바르게 호출되었는지 확인
        mock_send_message.assert_called_once_with(
            title='요청 거절',
            body=f'{trainer.trainer_name}님이 요청을 거절하였습니다.',
            token=user_fcm_token.fcm_token,  # 정확한 토큰 값을 확인하세요
            data={'change_ticket': data}
        )

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

    @patch('app.services.service_fcm.FcmService.send_message')
    def test_취소변경티켓이_승인된_경우(self, mock_send_message):
        user = TestDataFactory.create_user()
        user_fcm_token = TestDataFactory.create_user_fcm_token(user)
        trainer = TestDataFactory.create_trainer()
        trainer_user = TestDataFactory.create_trainer_user(trainer=trainer, user=user)
        schedule = TestDataFactory.create_schedule(trainer_user=trainer_user)

        lesson_current_count = trainer_user.lesson_current_count

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

        change_ticket_from_db = ChangeTicket.query.filter_by(id=cancel_change_ticket.id).first()
        schedule_from_db = Schedule.query.filter_by(schedule_id=schedule.schedule_id).first()
        trainer_user_from_db = TrainerUser.query.filter_by(trainer_user_id=trainer_user.trainer_user_id).first()

        self.assertEqual(200, response.status_code)
        self.assertEqual(const.CHANGE_TICKET_STATUS_APPROVED, change_ticket_from_db.status)
        self.assertEqual(const.SCHEDULE_CANCELLED, schedule_from_db.schedule_status)
        self.assertEqual(lesson_current_count + 1, trainer_user_from_db.lesson_current_count)

        # 푸시 알람이 올바르게 호출되었는지 확인
        mock_send_message.assert_called_once_with(
            title='요청 승인',
            body=f'{trainer.trainer_name}님이 요청을 승인하였습니다.',
            token=user_fcm_token.fcm_token,  # 정확한 토큰 값을 확인하세요
            data={'change_ticket': change_ticket_from_db}
        )

    @patch('app.services.service_fcm.FcmService.send_message')
    def test_시간변경티켓이_승인된_경우(self, mock_send_message):
        user = TestDataFactory.create_user()
        user_fcm_token = TestDataFactory.create_user_fcm_token(user)
        lesson_change_range = 1
        schedule_start_time = datetime.now() + timedelta(days=1, minutes=1)
        trainer = TestDataFactory.create_trainer(lesson_change_range=lesson_change_range)
        schedule = (ScheduleBuilder()
                    .with_user(user=user)
                    .with_trainer(trainer)
                    .with_start_time(schedule_start_time)
                    .build())

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
        print(response.get_json())

        change_ticket = ChangeTicket.query.filter_by(id=change_ticket.id).first()
        schedule = Schedule.query.filter_by(schedule_id=schedule.schedule_id).first()
        new_schedule = Schedule.query.filter_by(trainer_user_id=schedule.trainer_user_id,
                                                schedule_start_time=start_time).first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(change_ticket.status, const.CHANGE_TICKET_STATUS_APPROVED)
        self.assertEqual(schedule.schedule_status, const.SCHEDULE_MODIFIED)
        self.assertEqual(schedule.schedule_id, new_schedule.schedule_id)
        self.assertIsNotNone(new_schedule)

        mock_send_message.assert_called_once_with(
            title='요청 승인',
            body=f'{trainer.trainer_name}님이 요청을 승인하였습니다.',
            token=user_fcm_token.fcm_token,  # 정확한 토큰 값을 확인하세요
            data={'change_ticket': change_ticket}
        )

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

    @patch('app.services.service_fcm.FcmService.send_message')
    def test_변경티켓_시간에_이미_스케쥴이_있는데_수락하는_경우(self, mock_send_message):
        # Given
        user = TestDataFactory.create_user()
        lesson_change_range = 1
        trainer = TestDataFactory.create_trainer(lesson_change_range=lesson_change_range)
        trainer_user = TestDataFactory.create_trainer_user(trainer=trainer, user=user)

        already_exist_time = datetime.now() + timedelta(days=lesson_change_range, minutes=1)
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
            "start_time": already_exist_time.strftime(const.DATETIMEFORMAT)
        }

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.put(f'/change-ticket/{change_ticket.id}', headers=headers, json=body)

        # Then
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'],
                         'New schedule conflicts with existing schedules of the trainer')

        mock_send_message.assert_not_called()

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

    def test_이미_결정된_티켓을_삭제하면_400을_응답한다(self):
        user = TestDataFactory.create_user()
        change_ticket = ChangeTicketBuilder().with_user(user).with_status(CHANGE_TICKET_STATUS_APPROVED).build()

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.delete(f'/change-ticket/{change_ticket.id}', headers=headers)
        print(response.get_json())
        self.assertEqual(response.status_code, 400)
