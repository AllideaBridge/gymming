import http
from datetime import datetime, timedelta

import requests

from app import TrainerUser
from tests import BaseTestCase
from tests.test_data_factory import TestDataFactory


class TrainerUserTestCase(BaseTestCase):
    def test_트레이너의_회원_목록_조회(self):
        trainer = TestDataFactory.create_trainer()
        user_profile_data = b'user image file data'
        user_count = 3
        for _ in range(user_count):
            user = TestDataFactory.create_user()
            TestDataFactory.create_trainer_user(trainer, user)
            self.s3.put_object(Bucket='gymming', Key=f'user/{user.user_id}/profile', Body=user_profile_data)

        headers = TestDataFactory.create_trainer_auth_header(trainer.trainer_id)

        response = self.client.get(f'/trainer-user/trainer/{trainer.trainer_id}/users', headers=headers)
        print(response.get_json())

        data = response.get_json()
        results = data['results']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), user_count)
        for result in results:
            file_data = requests.get(result['user_profile_img_url']).content
            self.assertEqual(file_data, user_profile_data)

    def test_트레이너의_회원_상세_조회(self):
        trainer = TestDataFactory.create_trainer()
        user = TestDataFactory.create_user()
        TestDataFactory.create_trainer_user(trainer, user)
        user_profile_data = b'user image file data'
        self.s3.put_object(Bucket='gymming', Key=f'user/{user.user_id}/profile', Body=user_profile_data)

        headers = TestDataFactory.create_trainer_auth_header(trainer.trainer_id)

        response = self.client.get(f'/trainer-user/trainer/{trainer.trainer_id}/users/{user.user_id}', headers=headers)
        print(response.get_json())

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        file_data = requests.get(data['user_profile_img_url']).content
        self.assertEqual(file_data, user_profile_data)

    def test_유저의_트레이너_리스트_조회(self):
        user = TestDataFactory.create_user()
        trainer_profile_data = b'trainer image file data'
        trainer_count = 3
        for _ in range(trainer_count):
            trainer = TestDataFactory.create_trainer()
            TestDataFactory.create_trainer_user(trainer, user)
            self.s3.put_object(Bucket='gymming', Key=f'trainer/{trainer.trainer_id}/profile', Body=trainer_profile_data)

        headers = TestDataFactory.create_user_auth_header(user.user_id)
        response = self.client.get(f'/trainer-user/user/{user.user_id}/trainers', headers=headers)
        print(response.get_json())

        data = response.get_json()
        results = data['results']
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(results), trainer_count)
        for result in results:
            file_data = requests.get(result['trainer_profile_img_url']).content
            self.assertEqual(file_data, trainer_profile_data)

    def test_트레이닝_회원_등록(self):
        # Trainer 레코드 추가
        trainer = TestDataFactory.create_trainer()
        users = []
        for i in range(1, 4):
            user = TestDataFactory.create_user(
                name=f'User {i}'
            )
            users.append(user)

        headers = TestDataFactory.create_trainer_auth_header(trainer.trainer_id)
        for user in users:
            data = {
                'user_name': user.user_name,
                'phone_number': user.user_phone_number,
                'lesson_total_count': 10,
                'lesson_current_count': 10,
                'exercise_days': '월수금',
                'special_notice': '무릎 부상 주의'
            }

            response = self.client.post(f'/trainer-user/trainer/{trainer.trainer_id}/users',
                                        headers=headers, json=data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('새로운 회원이 등록됐습니다.', response.json['message'])

        results = TrainerUser.query.filter_by(trainer_id=trainer.trainer_id).all()
        self.assertEqual(3, len(results))

    def test_트레이닝_회원_모든데이터_수정(self):
        trainer = TestDataFactory.create_trainer()
        user = TestDataFactory.create_user()
        trainer_user = TestDataFactory.create_trainer_user(
            trainer=trainer,
            user=user
        )

        body = {
            'lesson_total_count': 3,
            'lesson_current_count': 3,
            'exercise_days': '월',
            'special_notice': '변경된 노트'
        }

        headers = TestDataFactory.create_trainer_auth_header(trainer.trainer_id)
        response = self.client.put(f'/trainer-user/trainer/{trainer.trainer_id}/users/{user.user_id}',
                                   headers=headers, json=body)

        self.assertEqual(response.status_code, http.HTTPStatus.OK)

        trainer_user_from_db = TrainerUser.query.filter_by(trainer_user_id=trainer_user.trainer_user_id).first()
        self.assertEqual(trainer_user_from_db.lesson_current_count, 3)
        self.assertEqual(trainer_user_from_db.lesson_total_count, 3)

        self.client.delete(f'/trainer-user/trainer/{trainer.trainer_id}/users/{user.user_id}', headers=headers,
                           json={
                               'trainer_user_id': trainer_user.trainer_user_id
                           })

        trainer_user_from_db = TrainerUser.query.filter_by(trainer_user_id=trainer_user.trainer_user_id).first()
        self.assertTrue(trainer_user_from_db.trainer_user_delete_flag)
