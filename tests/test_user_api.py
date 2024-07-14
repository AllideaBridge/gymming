import requests

from tests import BaseTestCase
from tests.test_data_factory import TestDataFactory


class UserTestCase(BaseTestCase):

    def test_유저_이름과_핸드폰번호로_조회(self):
        trainer = TestDataFactory.create_trainer()
        headers = TestDataFactory.create_trainer_auth_header(trainer.trainer_id)

        user_name = "ty"
        user_phone_number = "010-0001-5746"
        TestDataFactory.create_user(name=user_name, phone=user_phone_number)

        response = self.client.get(f'/users/check?user_name={user_name}&user_phone_number={user_phone_number}',
                                   headers=headers)

        self.assertEqual(response.status_code, 200)
        print(response.get_json())

    def test_유저_상세_조회_이미지_포함(self):
        user_name = "ty"
        user_phone_number = "010-0001-5746"
        user = TestDataFactory.create_user(name=user_name, phone=user_phone_number)
        headers = TestDataFactory.create_user_auth_header(user.user_id)
        self.s3.put_object(Bucket='gymming', Key=f'user/{user.user_id}/profile', Body=b'user image file data')

        response = self.client.get(f'/users/{user.user_id}', headers=headers)
        print(response.get_json())

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['user_name'], user_name)
        self.assertEqual(data['user_phone_number'], user_phone_number)
        file_data = requests.get(data['user_profile_img_url']).content
        self.assertEqual(file_data, b'user image file data')

    def test_유저_상세_조회_이미지_포함되지않음(self):
        user_name = "ty"
        user_phone_number = "010-0001-5746"
        user = TestDataFactory.create_user(name=user_name, phone=user_phone_number)
        headers = TestDataFactory.create_user_auth_header(user.user_id)

        response = self.client.get(f'/users/{user.user_id}', headers=headers)
        print(response.get_json())

        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['user_name'], user_name)
        self.assertEqual(data['user_phone_number'], user_phone_number)
