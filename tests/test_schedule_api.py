import unittest
from datetime import datetime, timedelta

from app import create_app, Users, Schedule, Trainer, TrainingUser
from app.common.constants import SCHEDULE_CANCELLED, SCHEDULE_SCHEDULED, DATETIMEFORMAT, SCHEDULE_MODIFIED
from database import db


class ScheduleTestCase(unittest.TestCase):
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

        # 사용자 데이터 생성
        user = Users(
            user_email="test@example.com",
            user_name="Test User",
            user_gender="M",
            user_phone_number="010-1234-5678",
            user_profile_img_url="http://example.com/profile.jpg"
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
                                    schedule_start_time=start_time + timedelta(days=j),
                                    schedule_status=SCHEDULE_SCHEDULED)
                db.session.add(schedule)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()

    def test_유저_한달_스케쥴_있는_날짜_조회(self):
        response = self.client.get('/schedules/user/1?date=2024-01-01&type=month')  # 2024년 1월의 스케줄을 요청
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['result'],
                         ['2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21',
                          '2024-01-22', '2024-01-23', '2024-01-24', '2024-01-25', '2024-01-26',
                          '2024-01-27', '2024-01-28', '2024-01-29', '2024-01-30', '2024-01-31'])
        print(response.get_json())

    def test_유저_하루_스케쥴_조회(self):
        response = self.client.get('/schedules/user/1?date=2024-01-21&type=day')
        print(response.get_json())
        self.assertEqual(len(response.get_json()['result']), 6)
        self.assertEqual(response.status_code, 200)

    def test_유저_스케쥴_변경(self):
        schedule_id = 1
        request_time = "2024-01-16 17:31:13"
        body = {
            "id": schedule_id,
            "start_time": request_time,
            "status": SCHEDULE_MODIFIED
        }
        response = self.client.put(f'/schedules/{schedule_id}', json=body)
        self.assertEqual(response.status_code, 200)

        schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        self.assertEqual(schedule.schedule_status, SCHEDULE_MODIFIED)
        self.assertEqual(schedule.schedule_start_time.strftime(DATETIMEFORMAT), request_time)

    def test_유저_없는_스케쥴_변경(self):
        schedule_id = 0
        request_time = datetime.now().strftime(DATETIMEFORMAT)
        body = {
            "id": schedule_id,
            "start_time": request_time,
            "status": SCHEDULE_MODIFIED
        }
        response = self.client.put(f'/schedules/{schedule_id}', json=body)
        self.assertEqual(response.status_code, 404)

    def test_유저_스케쥴_취소(self):
        schedule_id = 2
        schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        body = {
            "id": schedule_id,
            "start_time": schedule.schedule_start_time.strftime(DATETIMEFORMAT),
            "status": SCHEDULE_CANCELLED
        }
        response = self.client.put(f'/schedules/{schedule_id}', json=body)
        self.assertEqual(response.status_code, 200)

        schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        self.assertEqual(schedule.schedule_status, SCHEDULE_CANCELLED)

    def test_유저가_이미_있는_스케쥴로_변경하는_경우(self):
        schedule = Schedule.query.filter_by(schedule_status=SCHEDULE_SCHEDULED).first()
        schedule_id = schedule.schedule_id
        request_time = schedule.schedule_start_time.strftime(DATETIMEFORMAT)
        body = {
            "id": schedule_id,
            "start_time": request_time,
            "status": SCHEDULE_MODIFIED
        }
        response = self.client.put(f'/schedules/{schedule_id}', json=body)
        self.assertIn('conflict', response.get_json()['message'])

    def test_스케쥴_변경_가능(self):
        once_upon_a_time = datetime.now() + timedelta(days=4)
        schedule = Schedule(
            training_user_id=1,
            schedule_start_time=once_upon_a_time
        )
        db.session.add(schedule)
        db.session.commit()

        response = self.client.get(f'/schedules/user/{schedule.schedule_id}/check-change')
        self.assertTrue(response.get_json()["result"])
        self.assertEqual(response.get_json()["change_range"], 3)

    def test_스케쥴_변경_가능_경계값(self):
        once_upon_a_time = datetime.now() + timedelta(days=3) + timedelta(minutes=1)
        schedule = Schedule(
            training_user_id=1,
            schedule_start_time=once_upon_a_time
        )
        db.session.add(schedule)
        db.session.commit()

        response = self.client.get(f'/schedules/user/{schedule.schedule_id}/check-change')
        self.assertTrue(response.get_json()["result"])
        self.assertEqual(response.get_json()["change_range"], 3)

    def test_스케쥴_변경_불가능_경계값(self):
        once_upon_a_time = datetime.now() + timedelta(days=3) - timedelta(minutes=1)
        schedule = Schedule(
            training_user_id=1,
            schedule_start_time=once_upon_a_time
        )
        db.session.add(schedule)
        db.session.commit()

        response = self.client.get(f'/schedules/user/{schedule.schedule_id}/check-change')
        self.assertFalse(response.get_json()["result"])
        self.assertEqual(response.get_json()["change_range"], 3)

    def test_스케쥴_상세_조회(self):
        schedule_id = 1
        response = self.client.get(f'/schedules/{schedule_id}')
        data = response.get_json()
        self.assertIn("schedule_id", data)
        self.assertIn("schedule_start_time", data)
        self.assertIn("lesson_name", data)
        self.assertIn("trainer_name", data)
        self.assertIn("center_name", data)
        self.assertIn("center_location", data)
