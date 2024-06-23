import unittest
from app import create_app
from database import db
from tests.test_data_factory import TestDataFactory


class TrainerTestCase(unittest.TestCase):
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

    def test_put_트레이너(self):
        trainer = TestDataFactory.create_trainer()
        body = {
            "trainer_name": "test",
            "trainer_phone_number": "010-4444-4444",
            "trainer_gender": "M",
            "trainer_birthday": "1990-01-01",
            "description": "Hi",
            "lesson_name": "PT",
            "lesson_price": 30000,
            "lesson_change_range": 3,
            "center_name": "Center",
            "center_location": "Korea",
            "center_number": "02-555-5555",
            "center_type": "Weight",
            "trainer_availability": [
                {
                    # possible_lesson_cnt : 9
                    "week_day": 1,
                    "start_time": "09:00",
                    "end_time": "18:00"
                },
                {
                    # possible_lesson_cnt : 8
                    "week_day": 2,
                    "start_time": "12:30",
                    "end_time": "21:00"
                },
                {
                    # possible_lesson_cnt : 9
                    "week_day": 3,
                    "start_time": "12:00",
                    "end_time": "21:00"

                }
            ]
        }
        headers = TestDataFactory.create_trainer_auth_header(trainer.trainer_id)
        response = self.client.put(f'/trainers/{trainer.trainer_id}', headers=headers, json=body)

        self.assertEqual(response.status_code, 200)
