import requests

from tests import BaseTestCase
from tests.test_data_factory import TestDataFactory

from io import BytesIO


class TrainerTestCase(BaseTestCase):

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

    def test_트레이너_상세조회(self):
        trainer = TestDataFactory.create_trainer()
        TestDataFactory.create_trainer_availability(trainer=trainer)
        headers = TestDataFactory.create_trainer_auth_header(trainer.trainer_id)
        self.s3.put_object(Bucket='gymming', Key=f'trainer/{trainer.trainer_id}/profile',
                           Body=b'trainer image file data')

        response = self.client.get(f'/trainers/{trainer.trainer_id}', headers=headers)
        print(response.get_json())

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        file_data = requests.get(data['trainer_profile_img_url']).content
        self.assertEqual(file_data, b'trainer image file data')
