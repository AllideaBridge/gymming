import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from app import create_app, Users, Schedule, Trainer, TrainerUser, register_error_handlers
from app.common.constants import SCHEDULE_CANCELLED, SCHEDULE_SCHEDULED, DATETIMEFORMAT, SCHEDULE_MODIFIED
from app.common.exceptions import BadRequestError
from app.repositories.repository_trainer_user import TrainerUserRepository
from database import db
from tests import BaseTestCase
from tests.test_data_factory import ScheduleBuilder, TestDataFactory


class ScheduleTestCase(BaseTestCase):

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

    @patch('app.services.service_fcm.FcmService.send_message')
    def test_create_schedule_success(self, mock_send_message):
        # 준비
        trainer = TestDataFactory.create_trainer()
        user = TestDataFactory.create_user()
        trainer_fcm_token = TestDataFactory.create_trainer_fcm_token(trainer)

        # 수업 횟수가 남아있음
        lesson_current_count = 1
        trainer_user = TestDataFactory.create_trainer_user(trainer, user, lesson_current_count=lesson_current_count)

        data = {
            'trainer_id': trainer.trainer_id,
            'user_id': user.user_id,
            'schedule_start_time': (datetime.now() + timedelta(days=1)).strftime(DATETIMEFORMAT)
        }

        # 실행
        response = self.client.post('/schedules', json=data)

        # 검증
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], 'success')

        # 데이터베이스에 스케줄이 생성되었는지 확인
        created_schedule = db.session.query(Schedule).filter_by(
            trainer_user_id=trainer_user.trainer_user_id,
            schedule_start_time=datetime.strptime(data['schedule_start_time'], DATETIMEFORMAT)
        ).first()
        self.assertIsNotNone(created_schedule)
        self.assertEqual(created_schedule.schedule_status, SCHEDULE_SCHEDULED)

        # 수업 횟수가 차감되었는지 확인
        trainer_user_from_db = TrainerUserRepository(db=db).get(trainer_user.trainer_user_id)
        self.assertEqual(trainer_user_from_db.lesson_current_count, lesson_current_count - 1)

        # 푸시 알람이 올바르게 호출되었는지 확인
        mock_send_message.assert_called_once_with(
            title='수업 신청',
            body=f'{user.user_name}님이 수업을 신청하였습니다.',
            token=trainer_fcm_token.fcm_token,  # 정확한 토큰 값을 확인하세요
            data={'schedule_start_time': data['schedule_start_time']}
        )

    def test_과거시간으로_스케쥴을_생성하면_실패한다(self):
        # 준비
        trainer = TestDataFactory.create_trainer()
        user = TestDataFactory.create_user()
        # 수업 횟수가 남아있음
        lesson_current_count = 1
        trainer_user = TestDataFactory.create_trainer_user(trainer, user, lesson_current_count=lesson_current_count)

        data = {
            'trainer_id': trainer.trainer_id,
            'user_id': user.user_id,
            'schedule_start_time': (datetime.now()).strftime(DATETIMEFORMAT)
        }

        # 실행
        response = self.client.post('/schedules', json=data)
        print(response.get_json())
        # 검증
        self.assertEqual(response.status_code, 400)

    def test_create_schedule_conflict(self):
        # 준비
        trainer = TestDataFactory.create_trainer()
        user = TestDataFactory.create_user()
        # 수업 횟수가 남아있음
        lesson_current_count = 1
        TestDataFactory.create_trainer_user(trainer, user, lesson_current_count=lesson_current_count)

        # 이미 존재하는 스케줄 생성
        existing_schedule_time = datetime.now() + timedelta(days=1)
        ScheduleBuilder().with_trainer(trainer).with_user(user).with_start_time(existing_schedule_time).build()

        data = {
            'trainer_id': trainer.trainer_id,
            'user_id': user.user_id,
            'schedule_start_time': existing_schedule_time.strftime(DATETIMEFORMAT)
        }

        # 실행
        response = self.client.post('/schedules', json=data)

        # 검증
        self.assertEqual(response.status_code, 400)
        self.assertIn("Schedule is already exist", response.json['message'])

    def test_create_schedule_no_lessons_left(self):
        # 준비
        trainer = TestDataFactory.create_trainer()
        user = TestDataFactory.create_user()
        # 수업 횟수가 남지 않음
        lesson_current_count = 0
        TestDataFactory.create_trainer_user(trainer, user, lesson_current_count=lesson_current_count)

        data = {
            'trainer_id': trainer.trainer_id,
            'user_id': user.user_id,
            'schedule_start_time': (datetime.now() + timedelta(days=1)).strftime(DATETIMEFORMAT)
        }

        # 실행
        response = self.client.post('/schedules', json=data)

        # 검증
        self.assertEqual(response.status_code, 400)
        self.assertIn("There are no classes left", response.json['message'])
