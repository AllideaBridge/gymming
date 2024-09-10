from unittest.mock import patch

from app.entities.entity_trainer_refresh_token import TrainerRefreshToken
from app.entities.entity_user_refresh_token import UserRefreshToken
from tests import BaseTestCase
from tests.test_data_factory import TestDataFactory


class AuthTestCase(BaseTestCase):
    def test_트레이너_토큰으로_인증하면_trainer_id를_리턴한다(self):
        trainer = TestDataFactory.create_trainer()
        headers = TestDataFactory.create_trainer_auth_header(trainer.trainer_id)

        response = self.client.get(f'/auth/token-type-check', headers=headers)

        data = response.get_json()

        print(data)
        self.assertIn('trainer_id', data)

    def test_유저_토큰으로_인증하면_user_id를_리턴한다(self):
        user = TestDataFactory.create_user()
        headers = TestDataFactory.create_user_auth_header(user.user_id)

        response = self.client.get(f'/auth/token-type-check', headers=headers)

        data = response.get_json()

        print(data)
        self.assertIn('user_id', data)

    @patch('app.services.service_auth.AuthService.verify_kakao_token')
    @patch('app.services.service_auth.AuthService.get_kakao_user_info')
    def test_트레이너_로그인_성공하면_trainer_id와_토큰들을_리턴한다(self, get_kakao_user_info, verify_kakao_token):
        kakao_id = 123123214
        verify_kakao_token.return_value = True, ""
        get_kakao_user_info.return_value = {"id": kakao_id}

        trainer = TestDataFactory.create_trainer(trainer_social_id=f'kakao{kakao_id}')

        response = self.client.get(f'/auth/login/kakao/trainer?kakao_token=ttt')

        data = response.get_json()

        # 발급받은 refresh token은 DB에 저장되어야 함.
        trainer_refresh_token = TrainerRefreshToken.query.filter_by(trainer_id=trainer.trainer_id).first().refresh_token

        self.assertEqual(data['trainer_id'], trainer.trainer_id)
        self.assertEqual(data['refresh_token'], trainer_refresh_token)

    @patch('app.services.service_auth.AuthService.verify_kakao_token')
    @patch('app.services.service_auth.AuthService.get_kakao_user_info')
    def test_존재하지_않는_트레이너로_로그인하면_401을_응답한다(self, get_kakao_user_info, verify_kakao_token):
        kakao_id = 123123215
        verify_kakao_token.return_value = True, ""
        get_kakao_user_info.return_value = {"id": kakao_id}

        response = self.client.get(f'/auth/login/kakao/trainer?kakao_token=ttt')
        self.assertEqual(response.status_code, 401)

    @patch('app.services.service_auth.AuthService.verify_kakao_token')
    @patch('app.services.service_auth.AuthService.get_kakao_user_info')
    def test_유저_로그인_성공하면_user_id와_토큰들을_리턴한다(self, get_kakao_user_info, verify_kakao_token):
        kakao_id = 123123216
        verify_kakao_token.return_value = True, ""
        get_kakao_user_info.return_value = {"id": kakao_id}

        user = TestDataFactory.create_user(user_social_id=f'kakao{kakao_id}')

        response = self.client.get(f'/auth/login/kakao/user?kakao_token=ttt')

        data = response.get_json()

        # 발급받은 refresh token은 DB에 저장되어야 함.
        user_refresh_token = UserRefreshToken.query.filter_by(user_id=user.user_id).first().refresh_token

        self.assertEqual(data['user_id'], user.user_id)
        self.assertEqual(data['refresh_token'], user_refresh_token)

    @patch('app.services.service_auth.AuthService.verify_kakao_token')
    @patch('app.services.service_auth.AuthService.get_kakao_user_info')
    def test_존재하지_않는_유저로_로그인하면_401을_응답한다(self, get_kakao_user_info, verify_kakao_token):
        kakao_id = 123123217
        verify_kakao_token.return_value = True, ""
        get_kakao_user_info.return_value = {"id": kakao_id}

        response = self.client.get('/auth/login/kakao/user?kakao_token=ttt')
        self.assertEqual(response.status_code, 401)

    @patch('app.services.service_auth.AuthService.verify_kakao_token')
    @patch('app.services.service_auth.AuthService.get_kakao_user_info')
    def test_카카오_유저_회원가입이_성공하면_user_id와_토큰들을_응답한다(self, get_kakao_user_info, verify_kakao_token):
        kakao_id = 123123218
        verify_kakao_token.return_value = True, ""
        get_kakao_user_info.return_value = {"id": kakao_id}

        body = {
            'kakao_token': 'ttt',
            "user_name": "ty",
            "user_phone_number": "010-010-0010",
            "user_birthday": "1993-07-10",
            "user_gender": "F"
        }

        response = self.client.post('/auth/register/kakao/user', json=body)
        data = response.get_json()
        print(data)
        self.assertIn('user_id', data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

    @patch('app.services.service_auth.AuthService.verify_kakao_token')
    @patch('app.services.service_auth.AuthService.get_kakao_user_info')
    def test_이미_존재하는_카카오_유저로_회원가입하면_400을_응답한다(self, get_kakao_user_info, verify_kakao_token):
        kakao_id = 123123219
        verify_kakao_token.return_value = True, ""
        get_kakao_user_info.return_value = {"id": kakao_id}

        TestDataFactory.create_user(user_social_id=f'kakao{kakao_id}')

        body = {
            'kakao_token': 'ttt',
            "user_name": "ty",
            "user_phone_number": "010-010-0010",
            "user_birthday": "1993-07-10",
            "user_gender": "F"
        }

        response = self.client.post('/auth/register/kakao/user', json=body)
        data = response.get_json()
        print(data)
        self.assertEqual(response.status_code, 400)

    @patch('app.services.service_auth.AuthService.verify_kakao_token')
    @patch('app.services.service_auth.AuthService.get_kakao_user_info')
    def test_카카오_트레이너_회원가입이_성공하면_user_id와_토큰들을_응답한다(self, get_kakao_user_info, verify_kakao_token):
        kakao_id = 123123220
        verify_kakao_token.return_value = True, ""
        get_kakao_user_info.return_value = {"id": kakao_id}

        body = {
            'kakao_token': 'ttt',
            'trainer_name': 'trainer name',
            'trainer_phone_number': '010-0000-0000',
            'trainer_gender': 'M',
            'trainer_birthday': '1993-07-10',
            'description': '열심히 하겠습니다',
            'lesson_name': '헬스',
            'lesson_price': 30000,
            'lesson_change_range': 3,
            'center_name': 'gymming',
            'center_location': 'seoul',
            'center_number': '010-0000-0000',
            'center_type': '헬스장',
            'trainer_availability': [
                {
                    'week_day': 0,
                    'start_time': '09:00',
                    'end_time': '23:00'
                },
                {
                    'week_day': 1,
                    'start_time': '09:00',
                    'end_time': '15:00'
                },
                {
                    'week_day': 2,
                    'start_time': '09:00',
                    'end_time': '23:00'
                }

            ]
        }

        response = self.client.post('/auth/register/kakao/trainer', json=body)
        data = response.get_json()
        print(data)
        self.assertIn('trainer_id', data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)


    @patch('app.services.service_auth.AuthService.verify_kakao_token')
    @patch('app.services.service_auth.AuthService.get_kakao_user_info')
    def test_이미_존재하는_카카오_트레이너로_회원가입하면_400을_응답한다(self, get_kakao_user_info, verify_kakao_token):
        kakao_id = 123123221
        verify_kakao_token.return_value = True, ""
        get_kakao_user_info.return_value = {"id": kakao_id}

        TestDataFactory.create_trainer(trainer_social_id=f'kakao{kakao_id}')

        body = {
            'kakao_token': 'ttt',
            'trainer_name': 'trainer name',
            'trainer_phone_number': '010-0000-0000',
            'trainer_gender': 'M',
            'trainer_birthday': '1993-07-10',
            'description': '열심히 하겠습니다',
            'lesson_name': '헬스',
            'lesson_price': 30000,
            'lesson_change_range': 3,
            'center_name': 'gymming',
            'center_location': 'seoul',
            'center_number': '010-0000-0000',
            'center_type': '헬스장',
            'trainer_availability': [
                {
                    'week_day': 0,
                    'start_time': '09:00',
                    'end_time': '23:00'
                },
                {
                    'week_day': 1,
                    'start_time': '09:00',
                    'end_time': '15:00'
                },
                {
                    'week_day': 2,
                    'start_time': '09:00',
                    'end_time': '23:00'
                }

            ]
        }

        response = self.client.post('/auth/register/kakao/trainer', json=body)
        data = response.get_json()
        print(data)
        self.assertEqual(response.status_code, 400)
