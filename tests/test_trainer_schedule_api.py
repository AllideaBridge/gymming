import unittest
from datetime import datetime, timedelta

from app import create_app, Trainer, TrainingUser, Users, Schedule, TrainerAvailability
from app.common.Constants import DATETIMEFORMAT
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
            user = Users(user_name=f'Test User {i}', user_phone_number=f'010-1020-101{i}',
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

        # TrainerAvailability 레코드 추가
        for i in range(3):
            trainer_availability = TrainerAvailability(trainer_id=trainer.trainer_id, week_day=i + 1,
                                                       start_time=(start_time + timedelta(hours=i)).time(),
                                                       end_time=(start_time + timedelta(hours=9)).time(),
                                                       possible_lesson_cnt=2 + i)
            db.session.add(trainer_availability)

        db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()

    def test_트레이너_한달_스케쥴_정상(self):
        response = self.client.get('/schedules/trainer/1/2024/1')  # 예시 URL
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(),
                         ['2024-01-02', '2024-01-03', '2024-01-04', '2024-01-11', '2024-01-16', '2024-01-17',
                          '2024-01-18', '2024-01-23', '2024-01-24', '2024-01-25', '2024-01-30', '2024-01-31'])
        self.assertIsInstance(response.get_json(), list)

    def test_트레이너_근무시간_없는_경우(self):
        no_trainer_availability_trainer_id = 2
        response = self.client.get(f'/schedules/trainer/{no_trainer_availability_trainer_id}/2024/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_트레이너_하루_스케쥴(self):
        trainer_id = 1
        response = self.client.get(f'/schedules/trainer/{trainer_id}/2024/01/10')
        self.assertEqual(response.get_json(),
                         {'availability_end_time': '22:30', 'availability_start_time': '14:30', 'lesson_minutes': 60,
                          'lesson_change_range': 3,
                          'schedules': [{'schedule_id': 3, 'schedule_start_time': '2024-01-10 11:30:00'},
                                        {'schedule_id': 5, 'schedule_start_time': '2024-01-10 12:30:00'},
                                        {'schedule_id': 7, 'schedule_start_time': '2024-01-10 13:30:00'}]})

    def test_트레이너_일주일_스케쥴(self):
        trainer_id = 1
        response = self.client.get(f'/schedules/trainer/{trainer_id}/2024/01/7/week')
        results = response.get_json()
        for result in results:
            schedule_start_time = datetime.strptime(result['schedule_start_time'], DATETIMEFORMAT)
            self.assertTrue(datetime(2024, 1, 7) <= schedule_start_time <= datetime(2024, 1, 14),
                            msg="schedule_start_time이 지정된 날짜 범위 내에 없습니다.")
