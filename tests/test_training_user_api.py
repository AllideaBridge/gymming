import unittest
from datetime import datetime, timedelta

from app import create_app, Trainer, TrainingUser, Users, Schedule, TrainerAvailability
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

            response = self.client.post('/training-user/register', json=data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('새로운 회원이 등록되었습니다.', response.json['message'])

        response = self.client.get(f'/trainer/training_users?trainer_id={trainer.trainer_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), len(users))

        response = self.client.get(f'/trainer/training_users?trainer_id={trainer.trainer_id}&training_user_delete_flag=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 0)
