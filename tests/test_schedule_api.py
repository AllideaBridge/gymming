import unittest
from datetime import datetime, timedelta

from app import create_app, Users, Schedule, Trainer, TrainerUser
from app.common.constants import SCHEDULE_CANCELLED, SCHEDULE_SCHEDULED, DATETIMEFORMAT, SCHEDULE_MODIFIED
from database import db
from tests.test_data_factory import ScheduleBuilder, TestDataFactory


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

    def setUp(self):
        db.session.begin_nested()

    def tearDown(self):
        db.session.rollback()

    def test_유저_한달_스케쥴_있는_날짜_조회(self):
        user = TestDataFactory.create_user()
        schedules = []
        schedules.extend([ScheduleBuilder()
                         .with_user(user)
                         .with_start_time(datetime(2024, 1, 16) + timedelta(days=i))
                         .build()
                          for i in range(10)])

        schedules.extend([ScheduleBuilder()
                         .with_user(user)
                         .with_start_time(datetime(2024, 1, 23) + timedelta(days=i))
                         .build()
                          for i in range(10)])

        response = self.client.get(f'/schedules/user/{user.user_id}?date=2024-01-01&type=month')  # 2024년 1월의 스케줄을 요청
        result = response.get_json()['result']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result,
                         ['2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19', '2024-01-20', '2024-01-21',
                          '2024-01-22', '2024-01-23', '2024-01-24', '2024-01-25', '2024-01-26',
                          '2024-01-27', '2024-01-28', '2024-01-29', '2024-01-30', '2024-01-31'])

    def test_유저_하루_스케쥴_조회(self):
        user = TestDataFactory.create_user()
        schedules = [ScheduleBuilder()
                     .with_user(user)
                     .with_start_time(datetime(2024, 1, 21, 10) + timedelta(hours=i))
                     .build()
                     for i in range(10)]

        schedules.extend([ScheduleBuilder()
                         .with_user(user)
                         .with_start_time(datetime(2024, 1, 22, 12) + timedelta(hours=i))
                         .build()
                          for i in range(3)])

        response = self.client.get(f'/schedules/user/{user.user_id}?date=2024-01-21&type=day')
        print(response.get_json())
        result = response.get_json()['result']
        self.assertEqual(len(result), 10)
        self.assertEqual(response.status_code, 200)

    def test_유저_스케쥴_변경(self):
        schedule = (ScheduleBuilder()
                    .with_start_time(datetime(2024, 1, 22, 12))
                    .build())

        request_time = "2024-01-16 17:31:13"
        body = {
            "id": schedule.schedule_id,
            "start_time": request_time,
            "status": SCHEDULE_MODIFIED
        }
        response = self.client.put(f'/schedules/{schedule.schedule_id}', json=body)
        self.assertEqual(response.status_code, 200)

        schedule = Schedule.query.filter_by(schedule_id=schedule.schedule_id).first()
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
        schedule = (ScheduleBuilder()
                    .with_start_time(datetime(2024, 1, 22, 12))
                    .build())

        body = {
            "id": schedule.schedule_id,
            "start_time": schedule.schedule_start_time.strftime(DATETIMEFORMAT),
            "status": SCHEDULE_CANCELLED
        }
        response = self.client.put(f'/schedules/{schedule.schedule_id}', json=body)
        self.assertEqual(response.status_code, 200)

        schedule = Schedule.query.filter_by(schedule_id=schedule.schedule_id).first()
        self.assertEqual(schedule.schedule_status, SCHEDULE_CANCELLED)

    def test_유저가_이미_있는_트레이너의_스케쥴로_변경하는_경우(self):
        trainer = TestDataFactory.create_trainer()
        trainer_schedule = (ScheduleBuilder()
                            .with_trainer(trainer)
                            .with_start_time(datetime(2024, 1, 22, 12))
                            .build())

        user_schedule = (ScheduleBuilder()
                         .with_trainer(trainer)
                         .with_start_time(datetime(2024, 1, 22, 15))
                         .build())

        already_exist_time = trainer_schedule.schedule_start_time

        timedelta_range = [-30, 0, 30]

        for td in timedelta_range:
            body = {
                "id": user_schedule.schedule_id,
                "start_time": (already_exist_time + timedelta(minutes=td)).strftime(DATETIMEFORMAT),
                "status": SCHEDULE_MODIFIED
            }
            response = self.client.put(f'/schedules/{user_schedule.schedule_id}', json=body)
            self.assertIn('conflict', response.get_json()['message'])

    def test_스케쥴_변경_가능_validation(self):
        lesson_change_range = 3
        trainer = TestDataFactory.create_trainer(lesson_change_range=lesson_change_range)

        possible_time = datetime.now() + timedelta(days=lesson_change_range + 1)
        schedule = ScheduleBuilder().with_trainer(trainer).with_start_time(possible_time).build()

        response = self.client.get(f'/schedules/user/{schedule.schedule_id}/check-change')
        self.assertTrue(response.get_json()["result"])
        self.assertEqual(response.get_json()["change_range"], lesson_change_range)

    def test_스케쥴_변경_가능_validation_경계값(self):
        lesson_change_range = 3
        trainer = TestDataFactory.create_trainer(lesson_change_range=lesson_change_range)

        possible_time = datetime.now() + timedelta(days=lesson_change_range, minutes=1)
        schedule = ScheduleBuilder().with_trainer(trainer).with_start_time(possible_time).build()

        response = self.client.get(f'/schedules/user/{schedule.schedule_id}/check-change')
        self.assertTrue(response.get_json()["result"])
        self.assertEqual(response.get_json()["change_range"], lesson_change_range)

    def test_스케쥴_변경_불가능_경계값(self):
        lesson_change_range = 3
        trainer = TestDataFactory.create_trainer(lesson_change_range=lesson_change_range)

        possible_time = datetime.now() + timedelta(days=lesson_change_range, minutes=-1)
        schedule = ScheduleBuilder().with_trainer(trainer).with_start_time(possible_time).build()

        response = self.client.get(f'/schedules/user/{schedule.schedule_id}/check-change')
        self.assertFalse(response.get_json()["result"])
        self.assertEqual(response.get_json()["change_range"], 3)

    def test_스케쥴_상세_조회(self):
        schedule = ScheduleBuilder().build()
        response = self.client.get(f'/schedules/{schedule.schedule_id}')
        data = response.get_json()
        self.assertIn("schedule_id", data)
        self.assertIn("schedule_start_time", data)
        self.assertIn("lesson_name", data)
        self.assertIn("trainer_name", data)
        self.assertIn("center_name", data)
        self.assertIn("center_location", data)
