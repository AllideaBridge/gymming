import unittest
from datetime import datetime, timedelta

from app import create_app, Trainer, TrainingUser, Users, Schedule, Request
from app.common.Constants import REQUEST_TYPE_CANCEL, REQUEST_TYPE_MODIFY
from database import db


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
            user = Users(user_name=f'Test User {i}',
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
                request_cancel = Request(schedule_id=schedule.schedule_id, request_from='user',
                                         request_type=REQUEST_TYPE_CANCEL)
                db.session.add(request_cancel)
                request_modify = Request(schedule_id=schedule.schedule_id, request_from='user',
                                         request_type=REQUEST_TYPE_MODIFY, request_time=datetime.now())
                db.session.add(request_modify)
                db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()

    def test_트레이너_요청_리스트_조회(self):
        trainer_id = 1
        response = self.client.get(f'/request/trainer/{trainer_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        if data:
            for req in data:
                r = db.session.query(TrainingUser.trainer_id) \
                    .join(Schedule, Schedule.training_user_id == TrainingUser.training_user_id) \
                    .join(Request, Request.schedule_id == Schedule.schedule_id) \
                    .filter(Request.request_id == req['request_id']) \
                    .first()
                self.assertEqual(r[0], trainer_id)
