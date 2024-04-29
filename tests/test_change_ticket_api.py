import unittest
from datetime import datetime, timedelta

from app import create_app, Trainer, TrainingUser, Users, Schedule, ChangeTicket
from app.common.constants import CHANGE_TICKET_TYPE_CANCEL, CHANGE_TICKET_TYPE_MODIFY, CHANGE_TICKET_STATUS_WAITING, \
    CHANGE_TICKET_STATUS_REJECTED, CHANGE_TICKET_STATUS_APPROVED, SCHEDULE_CANCELLED, SCHEDULE_MODIFIED, SCHEDULE_SCHEDULED
from database import db

URL_CHANGE_TICKET_APPROVED = '/change-ticket/approve'


class TrainerScheduleTestCase(unittest.TestCase):
    app = None
    app_context = None

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('test')
        cls.app_context = cls.app.app_context()
        # Todo : 컨텍스트 활성화 좀 더 찾아보기
        cls.app_context.push()
        db.drop_all()
        db.create_all()
        cls.client = cls.app.test_client()

        # Trainer 레코드 추가
        trainer = Trainer(trainer_name='Test Trainer', trainer_email='test@example.com',
                          trainer_gender='M', trainer_phone_number='010-0000-0000', lesson_minutes=60,
                          lesson_change_range=3)
        db.session.add(trainer)
        db.session.commit()

        # Users, TrainingUser, Schedule 레코드 추가
        for i in range(1, 4):
            user = Users(user_name=f'Test User {i}', user_phone_number= f'010-1020-101{i}',
                         user_email=f'user{i}@example.com', user_login_platform='platform')  # 필드는 Users 모델에 맞게 조정
            db.session.add(user)
            db.session.commit()
            training_user = TrainingUser(trainer_id=trainer.trainer_id, user_id=user.user_id)
            db.session.add(training_user)
            db.session.commit()
            start_time = datetime(2024, 1, 7 + i, 10 + i, 30)
            for j in range(3):
                schedule = Schedule(training_user_id=training_user.training_user_id,
                                    schedule_start_time=start_time + timedelta(days=j))
                db.session.add(schedule)
                db.session.commit()
                change_ticket_cancel = ChangeTicket(schedule_id=schedule.schedule_id, change_from='user',
                                              change_type=CHANGE_TICKET_TYPE_CANCEL,
                                              description=f'Change ticket cancel description {j}',
                                              status=CHANGE_TICKET_STATUS_WAITING)
                db.session.add(change_ticket_cancel)
                change_ticket_modify = ChangeTicket(schedule_id=schedule.schedule_id, change_from='user',
                                              change_type=CHANGE_TICKET_TYPE_MODIFY, request_time=datetime.now(),
                                              description=f'Change ticket modify description {j}',
                                              status=CHANGE_TICKET_STATUS_WAITING)
                db.session.add(change_ticket_modify)
                db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()

    def test_트레이너_요청_대기_리스트_조회(self):
        trainer_id = 1
        response = self.client.get(f'/change-ticket/trainer?trainer_id={trainer_id}&status={CHANGE_TICKET_STATUS_WAITING}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        if data:
            for req in data:
                r = db.session.query(TrainingUser.trainer_id, ChangeTicket.status) \
                    .join(Schedule, ChangeTicket.schedule_id == Schedule.schedule_id) \
                    .join(TrainingUser, Schedule.training_user_id == TrainingUser.training_user_id) \
                    .filter(ChangeTicket.id == req['id']) \
                    .first()
                self.assertEqual(r[0], trainer_id)
                self.assertEqual(r[1], CHANGE_TICKET_STATUS_WAITING)

    def test_트레이너_요청_완료_리스트_조회(self):
        trainer_id = 1
        response = self.client.get(
            f'/change-ticket/trainer?trainer_id={trainer_id}&status={CHANGE_TICKET_STATUS_APPROVED},{CHANGE_TICKET_STATUS_REJECTED}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        if data:
            for req in data:
                r = db.session.query(TrainingUser.trainer_id, ChangeTicket.status) \
                    .join(Schedule, ChangeTicket.schedule_id == Schedule.schedule_id) \
                    .join(TrainingUser, Schedule.training_user_id == TrainingUser.training_user_id) \
                    .filter(ChangeTicket.id == req['id']) \
                    .first()
                self.assertEqual(r[0], trainer_id)
                self.assertIn(r[1], [CHANGE_TICKET_STATUS_APPROVED, CHANGE_TICKET_STATUS_REJECTED])

    def test_유효하지_않은_파라미터로_트레이너_요청_리스트_조회(self):
        trainer_id = 1
        response = self.client.get(
            f'/change-ticket/trainer?trainer_id={trainer_id}&status={CHANGE_TICKET_STATUS_WAITING},{CHANGE_TICKET_STATUS_REJECTED}')
        self.assertEqual(response.status_code, 400)

    def test_요청_상세조회(self):
        change_ticket_id = 1
        response = self.client.get(f'/change-ticket/{change_ticket_id}/details')
        data = response.get_json()
        self.assertEqual(data['change_ticket_id'], change_ticket_id)
        self.assertIn('description', data, msg='description is missing in response')

    def test_없는_요청_상세조회(self):
        change_ticket_id = 0
        response = self.client.get(f'/change-ticket/{change_ticket_id}/details')
        self.assertEqual(response.status_code, 404)

    def test_요청_거절(self):
        change_ticket_id = 1
        reject_reason = "reject reason"
        body = {
            "id": change_ticket_id,
            "reject_reason": reject_reason
        }
        self.client.put('/change-ticket/reject', json=body)

        data = ChangeTicket.query.filter_by(id=change_ticket_id).first()
        self.assertEqual(change_ticket_id, data.id)
        self.assertEqual(CHANGE_TICKET_STATUS_REJECTED, data.status)
        self.assertEqual(reject_reason, data.reject_reason)

    def test_유효하지_않은_change_type으로_승인_요청한_경우(self):
        body = {
            'change_ticket_id': 1,
            'change_type': "invalid_change_type"
        }
        response = self.client.post(URL_CHANGE_TICKET_APPROVED, json=body)
        self.assertEqual(response.status_code, 400)

    def test_취소_요청이_승인된_경우(self):
        change_ticket = ChangeTicket.query.filter_by(change_type=CHANGE_TICKET_TYPE_CANCEL,
                                               status=CHANGE_TICKET_STATUS_WAITING).first()
        change_ticket_id = change_ticket.id
        schedule_id = change_ticket.schedule_id
        body = {
            'change_ticket_id': change_ticket_id,
            'change_type': CHANGE_TICKET_TYPE_CANCEL
        }
        response = self.client.post(URL_CHANGE_TICKET_APPROVED, json=body)
        change_ticket = ChangeTicket.query.filter_by(change_ticket_id=change_ticket_id).first()
        schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(change_ticket.status, CHANGE_TICKET_STATUS_APPROVED)
        self.assertEqual(schedule.schedule_status, SCHEDULE_CANCELLED)

    def test_수정_요청이_승인된_경우(self):
        change_ticket = ChangeTicket.query.filter_by(change_type=CHANGE_TICKET_TYPE_MODIFY,
                                               status=CHANGE_TICKET_STATUS_WAITING).first()
        change_ticket_id = change_ticket.id
        schedule_id = change_ticket.schedule_id
        body = {
            'id': change_ticket_id,
            'change_type': CHANGE_TICKET_TYPE_MODIFY
        }
        response = self.client.post(URL_CHANGE_TICKET_APPROVED, json=body)
        change_ticket = ChangeTicket.query.filter_by(id=change_ticket_id).first()
        schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        new_schedule = Schedule.query.filter_by(training_user_id=schedule.training_user_id,
                                                schedule_start_time=change_ticket.request_time).first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(change_ticket.status, CHANGE_TICKET_STATUS_APPROVED)
        self.assertEqual(schedule.schedule_status, SCHEDULE_MODIFIED)
        self.assertIsNotNone(new_schedule)

    def test_요청_상태가_WAITING이_아닌_경우(self):
        change_ticket = ChangeTicket.query.filter_by(change_type=CHANGE_TICKET_TYPE_MODIFY,
                                               status=CHANGE_TICKET_STATUS_APPROVED).first()
        change_ticket_id = change_ticket.id
        body = {
            'change_ticket_id': change_ticket_id,
            'change_type': CHANGE_TICKET_TYPE_MODIFY
        }
        response = self.client.post(URL_CHANGE_TICKET_APPROVED, json=body)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'], 'Invalid Change ticket Status')

    def test_요청_시간에_이미_스케쥴이_있는_경우(self):
        change_ticket = ChangeTicket.query.filter_by(change_type=CHANGE_TICKET_TYPE_MODIFY,
                                               status=CHANGE_TICKET_STATUS_WAITING).first()
        change_ticket_id = change_ticket.id
        schedule_id = change_ticket.schedule_id
        schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        already_exist_schedule = Schedule(training_user_id=schedule.training_user_id,
                                          schedule_start_time=str(change_ticket.request_time),
                                          schedule_status=SCHEDULE_SCHEDULED)
        db.session.add(already_exist_schedule)
        db.session.commit()

        body = {
            'change_ticket_id': change_ticket_id,
            'change_type': CHANGE_TICKET_TYPE_MODIFY
        }
        response = self.client.post(URL_CHANGE_TICKET_APPROVED, json=body)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()['message'],
                         'New schedule conflicts with existing schedules of the trainer')
