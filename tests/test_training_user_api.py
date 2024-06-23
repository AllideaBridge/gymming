import http
import unittest
from datetime import datetime, timedelta

from app import create_app, Trainer, TrainerUser, Users, Schedule
from app.common.constants import DATEFORMAT
from database import db


class TrainerUserTestCase(unittest.TestCase):
    app = None
    app_context = None

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('test')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.drop_all()
        db.create_all()
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()

    def test_트레이닝_회원_등록(self):
        # Trainer 레코드 추가
        trainer = Trainer(trainer_name='Test Trainer', trainer_email='test@example.com',
                          trainer_gender='M', trainer_phone_number='010-0000-0000', lesson_minutes=60,
                          lesson_change_range=3)
        db.session.add(trainer)
        db.session.commit()

        users = []
        # Users 레코드 추가
        for i in range(1, 4):
            user = Users(user_name=f'Test User {i}', user_phone_number=f'010-1234-123{i}',
                         user_email=f'user{i}@example.com', user_login_platform='platform')  # 필드는 Users 모델에 맞게 조정
            users.append(user)
            db.session.add(user)
        db.session.commit()

        for user in users:
            data = {
                'trainer_id': trainer.trainer_id,
                'user_name': user.user_name,
                'user_phone_number': user.user_phone_number,
                'lesson_total_count': 10,
                'exercise_days': '월수금',
                'special_notes': '무릎 부상 주의'
            }

            response = self.client.post('/trainer/trainer-user/user', json=data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('새로운 회원이 등록되었습니다.', response.json['message'])

        response = self.client.get(f'/trainer/trainer-user?trainer_id={trainer.trainer_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), len(users))

        response = self.client.get(
            f'/trainer/trainer-user?trainer_id={trainer.trainer_id}&trainer_user_delete_flag=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)

    def test_트레이닝_회원_조회(self):
        # Trainer 레코드 추가
        trainer = Trainer(trainer_name='Test Trainer', trainer_email='test@example.com',
                          trainer_gender='M', trainer_phone_number='010-0000-0000', lesson_minutes=60,
                          lesson_change_range=3)
        db.session.add(trainer)
        db.session.commit()

        # Users 데이터 생성
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

        # TrainingUser 데이터 생성
        trainer_user = TrainerUser(trainer_id=trainer.trainer_id, user_id=user.user_id)
        db.session.add(trainer_user)
        db.session.commit()

        # Schedule 데이터 생성
        schedules = []
        start_time = datetime(2024, 1, 15)
        for i in range(10):
            schedule = Schedule(trainer_user_id=trainer_user.trainer_user_id,
                                schedule_start_time=start_time + timedelta(days=i))
            db.session.add(schedule)
            schedules.append(schedule)
        db.session.commit()

        response = self.client.get(
            f'/schedules/trainer/{trainer_user.trainer_id}/users/{trainer_user.user_id}?date=2024-01-01&type=month')
        print(response.get_json())
        data = response.get_json()["result"]
        self.assertEqual(len(data), len(schedules))
        for schedule in schedules:
            response = self.client.get(f'/trainer/trainer-user/schedule/{schedule.schedule_id}')
            data = response.get_json()
            self.assertEqual(schedule.schedule_start_time.strftime(DATEFORMAT), data["schedule_start_time"])
            self.assertEqual(schedule.schedule_status, data["schedule_status"])

        response = self.client.get(f'/users/{user.user_id}')
        data = response.get_json()
        self.assertEqual(user.user_id, data['user_id'])
        self.assertEqual(user.user_email, data['user_email'])
        self.assertEqual(user.user_name, data['user_name'])
        self.assertEqual(user.user_gender, data['user_gender'])
        self.assertEqual(user.user_phone_number, data['user_phone_number'])
        self.assertEqual(user.user_profile_img_url, data['user_profile_img_url'])
        self.assertEqual(user.user_delete_flag, data['user_delete_flag'])
        self.assertEqual(user.user_login_platform, data['user_login_platform'])
        self.assertEqual(user.user_birthday, data['user_birthday'])

    def test_트레이닝_회원_수정(self):
        # Trainer 레코드 추가
        trainer = Trainer(trainer_name='Test Trainer', trainer_email='test@example.com',
                          trainer_gender='M', trainer_phone_number='010-0000-0000', lesson_minutes=60,
                          lesson_change_range=3)
        db.session.add(trainer)
        db.session.commit()

        # Users 데이터 생성
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

        # TrainingUser 데이터 생성
        trainer_user = TrainerUser(trainer_id=trainer.trainer_id, user_id=user.user_id)
        db.session.add(trainer_user)
        db.session.commit()

        trainer_user_id = trainer_user.trainer_user_id
        lesson_total_count = 10
        lesson_current_count = 10
        response = self.client.put('/trainer/trainer-user/user', json={
            'trainer_user_id': trainer_user_id,
            'lesson_total_count': lesson_total_count,
            'lesson_current_count': lesson_current_count
        })

        self.assertEqual(response.status_code, http.HTTPStatus.OK)

        trainer_user_from_db = TrainerUser.query.filter_by(trainer_user_id=trainer_user_id).first()
        self.assertEqual(trainer_user_from_db.lesson_current_count, lesson_current_count)
        self.assertEqual(trainer_user_from_db.lesson_total_count, lesson_total_count)

        self.client.delete('/trainer/trainer-user/user', json={
            'trainer_user_id': trainer_user_id
        })

        trainer_user_from_db = TrainerUser.query.filter_by(trainer_user_id=trainer_user_id).first()
        self.assertTrue(trainer_user_from_db.trainer_user_delete_flag)
