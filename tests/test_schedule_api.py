import unittest
from datetime import datetime, timedelta
from random import randint

from app import create_app, Users, Schedule, Trainer, Center, TrainingUser
from app.common.Constants import SCHEDULE_CANCELLED, SCHEDULED
from database import db


class ScheduleTestCase(unittest.TestCase):
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

        # 사용자 데이터 생성
        user = Users(
            user_email="test@example.com",
            user_name="Test User",
            user_gender="M",
            user_phone_number="010-1234-5678",
            user_profile_img_url="http://example.com/profile.jpg",
            user_login_platform="test_platform"
        )
        db.session.add(user)
        db.session.commit()

        # 트레이너 데이터 생성
        for i in range(1, 10):
            trainer = Trainer(
                trainer_name=f'Test Trainer{i}',
                trainer_email='test@example.com',
                trainer_gender='M',
                trainer_phone_number='010-0000-0000',
                lesson_minutes=60,
                lesson_change_range=3
            )
            db.session.add(trainer)
            db.session.commit()
            training_user = TrainingUser(trainer_id=trainer.trainer_id, user_id=user.user_id)
            db.session.add(training_user)
            db.session.commit()
            start_time = datetime(2024, 1, 15 + i)
            for j in range(10):
                schedule = Schedule(training_user_id=training_user.training_user_id,
                                    schedule_start_time=start_time + timedelta(days=j))
                db.session.add(schedule)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()

    def test_유저_한달_스케쥴_있는_날짜_조회(self):
        response = self.client.get('/schedules/1/2024/1')  # 2024년 1월의 스케줄을 요청
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(),
                         ['2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21',
                          '2024-01-22', '2024-01-23', '2024-01-24', '2024-01-25', '2024-01-26',
                          '2024-01-27', '2024-01-28', '2024-01-29', '2024-01-30', '2024-01-31'])
        print(response.get_json())

    def test_유저_하루_스케쥴_조회(self):
        response = self.client.get('/schedules/1/2024/1/21')
        self.assertEqual(len(response.get_json()), 6)
        print(response.get_json())
        self.assertEqual(response.status_code, 200)

    def test_유저_스케쥴_변경(self):
        schedule_id = 1
        requested_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        body = {
            'requested_date': requested_date
        }
        response = self.client.post(f'/schedules/{schedule_id}/change', json=body)
        self.assertEqual(response.status_code, 200)

        old_schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        self.assertEqual(old_schedule.schedule_status, SCHEDULE_CANCELLED)

        new_schedule = Schedule.query.filter_by(schedule_start_time=requested_date).first()
        self.assertEqual(new_schedule.schedule_status, SCHEDULED)

    def test_유저_없는_스케쥴_변경(self):
        schedule_id = 0
        requested_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        body = {
            'requested_date': requested_date
        }
        response = self.client.post(f'/schedules/{schedule_id}/change', json=body)
        self.assertEqual(response.status_code, 404)

    def test_유저_스케쥴_취소(self):
        schedule_id = 2
        response = self.client.post(f'/schedules/{schedule_id}/cancel')
        self.assertEqual(response.status_code, 200)

        old_schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        self.assertEqual(old_schedule.schedule_status, SCHEDULE_CANCELLED)