from calendar import monthrange
from datetime import datetime, timedelta

from app.common.constants import DATEFORMAT, SCHEDULE_MODIFIED, SCHEDULE_CANCELLED, SCHEDULE_TYPE_MONTH, \
    SCHEDULE_TYPE_DAY, SCHEDULE_TYPE_WEEK, DATETIMEFORMAT, SCHEDULE_SCHEDULED
from app.common.exceptions import BadRequestError, ApplicationError, ResourceNotFound
from app.entities.entity_schedule import Schedule


class ScheduleService:

    def __init__(self, schedule_repository, trainer_availability_repository, trainer_user_repository,
                 trainer_repository, message_service, trainer_fcm_token_repository, user_repository):
        self.schedule_repository = schedule_repository
        self.trainer_availability_repository = trainer_availability_repository
        self.trainer_user_repository = trainer_user_repository
        self.trainer_repository = trainer_repository
        self.message_service = message_service
        self.trainer_fcm_token_repository = trainer_fcm_token_repository
        self.user_repository = user_repository

    def handle_get_user_schedule(self, user_id, date_str, schedule_type):
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        year = date_obj.year
        month = date_obj.month
        day = date_obj.day

        if schedule_type == SCHEDULE_TYPE_MONTH:
            return self.get_user_month_schedule_date(user_id, year, month)

        if schedule_type == SCHEDULE_TYPE_DAY:
            return self.get_user_day_schedule(user_id, year, month, day)

        raise BadRequestError

    def get_user_month_schedule_date(self, user_id, year, month):
        schedules = self.schedule_repository.select_month_schedule_time_by_user_id(user_id, year, month)
        scheduled_dates = [schedule[0].strftime(DATEFORMAT) for schedule in schedules] if schedules else []
        return {"result": scheduled_dates}

    def get_user_day_schedule(self, user_id, year, month, day):
        results = self.schedule_repository.select_day_schedule_by_user_id(user_id, year, month, day)

        data = []
        for row in results:
            item = {
                "schedule_id": row.schedule_id,
                "trainer_id": row.trainer_id,
                "schedule_start_time": row.schedule_start_time.strftime(DATETIMEFORMAT),
                "lesson_name": row.lesson_name,
                "trainer_name": row.trainer_name,
                "center_name": row.center_name,
                "center_location": row.center_location,
                "lesson_change_range": row.lesson_change_range,
                "lesson_minutes": row.lesson_minutes
            }
            data.append(item)

        return {"result": data}


    def handle_change_user_schedule(self, schedule_id, start_time, status):
        if status == SCHEDULE_MODIFIED:
            return self._change_schedule(schedule_id, start_time)
        if status == SCHEDULE_CANCELLED:
            return self._cancel_schedule(schedule_id)
        raise BadRequestError

    def _change_schedule(self, schedule_id, start_time):
        # 스케쥴 변경 가능 범위인지 확인.
        # todo : 성민이 에지케이스
        changeable = self.validate_schedule_change(schedule_id=schedule_id).get('result')
        if changeable is None or not changeable:
            raise BadRequestError(
                message=f'Schedule is not changeable.Lesson change range overflow. schedule_id : {schedule_id}')

        schedule = self.schedule_repository.get(schedule_id)
        if not schedule:
            raise ApplicationError(f"Schedule not found {schedule_id}", 404)

        trainer_user = self.trainer_user_repository.get(schedule.trainer_user_id)
        trainer_id = trainer_user.trainer_id

        conflict_schedule = self.schedule_repository.select_conflict_trainer_schedule_by_time(trainer_id, start_time)

        if conflict_schedule:
            # 충돌하는 스케줄이 있는 경우
            raise ApplicationError(f"New schedule conflicts with existing schedules of the trainer", 400)

        schedule.schedule_status = SCHEDULE_MODIFIED
        schedule.schedule_start_time = start_time
        self.schedule_repository.update(schedule)
        return {'message': 'Schedule updated successfully'}, 200

    def _cancel_schedule(self, schedule_id):
        schedule = self.schedule_repository.get(schedule_id)

        if not schedule:
            raise ApplicationError(f"Schedule not found {schedule_id}", 404)

        schedule.schedule_status = SCHEDULE_CANCELLED
        lesson = schedule.lesson
        lesson.lesson_current_count += 1
        self.schedule_repository.update(schedule)
        return {'message': 'Schedule cancel successfully'}, 200

    def delete_schedule(self, schedule_id):
        # todo.txt : 스케쥴 변경 가능 범위인지 확인.
        schedule = self.schedule_repository.get(schedule_id)
        deleted = self.schedule_repository.delete(schedule)
        if deleted:
            return {"message": "Schedule deleted successfully."}, 200
        raise ApplicationError(f"Schedule not found {schedule_id}", 404)

    def handle_get_trainer_schedule(self, trainer_id, date, type):
        if type == SCHEDULE_TYPE_DAY:
            return self.get_trainer_day_schedule(trainer_id, date)

        if type == SCHEDULE_TYPE_WEEK:
            return self.get_trainer_week_schedule(trainer_id, date)

        if type == SCHEDULE_TYPE_MONTH:
            return self.get_trainer_month_schedule(trainer_id, date)

        raise BadRequestError

    def get_trainer_month_schedule(self, trainer_id, date):
        year = date.year
        month = date.month

        # 1단계: 트레이너의 전체 가능 요일 조회
        available_week_days = self.trainer_availability_repository.select_week_day_by_trainer_id(trainer_id)

        if not available_week_days:
            return []

        available_week_days = set([week_day for week_day, in available_week_days])

        # 2단계: 해당 월의 모든 날짜를 순회하며 "근무 가능 날짜" 목록 생성
        available_dates = set()
        num_days = monthrange(year, month)[1]
        for day in range(1, num_days + 1):
            candidate_date = datetime(year, month, day)
            if candidate_date.weekday() in available_week_days:
                available_dates.add(candidate_date.strftime(DATEFORMAT))

        # 3단계: 조건을 충족 하는 날짜 조회 및 "근무 가능 날짜"에서 제외
        full_dates = self.schedule_repository.select_full_date_by_trainer_id_and_year_month(trainer_id, year, month)
        for full_date, in full_dates:
            available_dates.discard(full_date.strftime(DATEFORMAT))

        # "근무 가능 날짜" 목록에서 조건을 충족하는 날짜를 제외한 결과 반환
        return {
            'result': sorted(list(available_dates))
        }

    def get_trainer_week_schedule(self, trainer_id, date):
        start_date = date
        end_date = date + timedelta(days=6)

        schedules = self.schedule_repository.select_week_schedule_by_trainer_id(trainer_id, start_date, end_date)
        trainer = self.trainer_repository.get(trainer_id)

        result = {
            'result': [
                {
                    'user_id': s.user_id,
                    'user_name': s.user_name,
                    'schedule_start_time': s.schedule_start_time.strftime(DATETIMEFORMAT)
                } for s in schedules
            ],
            'lesson_minute': trainer.lesson_minutes
        }

        return result

    def get_trainer_day_schedule(self, trainer_id, date):
        trainer_details = self.trainer_repository.select_trainer_details_by_id_and_date(trainer_id, date)

        if not trainer_details:
            return {'result': []}

        start_dt = datetime.combine(date, trainer_details.start_time)
        end_dt = datetime.combine(date, trainer_details.end_time)

        time_slots = []
        current_time = start_dt

        while current_time + timedelta(minutes=30) <= end_dt:
            time_slots.append(current_time)
            current_time += timedelta(minutes=30)

        schedules = self.schedule_repository.select_day_schedule_by_trainer_id(trainer_id=trainer_id, date=date)

        scheduled_times = [
            (s.schedule_start_time, s.schedule_start_time + timedelta(minutes=trainer_details.lesson_minutes))
            for s in schedules
        ]

        result = []
        for slot in time_slots:
            is_available = not any(
                s[0] <= slot < s[1] for s in scheduled_times
            )
            result.append({
                'time': slot.strftime('%H:%M'),
                'possible': is_available
            })

        return {'result': result}

    def get_trainer_user_schedule(self, trainer_id, user_id, date, query_type):
        if query_type == SCHEDULE_TYPE_MONTH:
            start_date = datetime(date.year, date.month, 1)
            if date.month == 12:
                end_date = datetime(date.year + 1, 1, 1)
            else:
                end_date = datetime(date.year, date.month + 1, 1)

            schedules = self.schedule_repository.select_month_schedule_by_user_id_and_trainer_id(trainer_id, user_id,
                                                                                                 start_date, end_date)
            return [{"schedule_id": schedule.schedule_id,
                     "schedule_start_time": schedule.schedule_start_time.strftime(DATETIMEFORMAT)} for
                    schedule in schedules]

        raise BadRequestError

    def validate_schedule_change(self, schedule_id):
        schedule = self.schedule_repository.select_schedule_by_schedule_id(schedule_id)

        if schedule is None:
            raise ResourceNotFound(message="스케쥴이 존재하지 않습니다.")

        lesson_change_range = schedule.lesson_change_range

        current_time = datetime.now()
        diff = schedule.schedule_start_time - current_time

        if current_time <= schedule.schedule_start_time and timedelta(days=lesson_change_range) <= diff:
            return {
                "result": True,
                "change_range": lesson_change_range
            }

        return {
            "result": False,
            "change_range": lesson_change_range
        }

    def get_schedule_details(self, schedule_id):
        schedule = self.schedule_repository.select_schedule_by_schedule_id(schedule_id)

        return {
            "schedule_id": schedule.schedule_id,
            "schedule_start_time": schedule.schedule_start_time.strftime(DATETIMEFORMAT),
            "lesson_name": schedule.lesson_name,
            "trainer_name": schedule.trainer_name,
            "center_name": schedule.center_name,
            "center_location": schedule.center_location,
        }

    def create_schedule(self, body):
        trainer_id = body.trainer_id
        user_id = body.user_id
        schedule_start_time = datetime.strptime(body.schedule_start_time, DATETIMEFORMAT)
        trainer_user = self.trainer_user_repository.select_by_trainer_id_and_user_id(trainer_id, user_id)
        if not trainer_user:
            raise BadRequestError("Trainer-User relationship not found")

        # 스케쥴 충돌 여부
        conflict_schedule = self.schedule_repository.select_conflict_schedule_by_trainer_id_and_request_time(trainer_id,
                                                                                                             schedule_start_time)
        if conflict_schedule is not None:
            raise BadRequestError("Schedule is already exist")

        # 수업 카운트 차감
        if trainer_user.lesson_current_count < 1:
            raise BadRequestError("There are no classes left.")

        trainer_user.lesson_current_count -= 1

        schedule = Schedule(
            trainer_user_id=trainer_user.trainer_user_id,
            schedule_start_time=schedule_start_time,
            schedule_status=SCHEDULE_SCHEDULED
        )

        # 스케쥴 생성
        self.schedule_repository.create(schedule)

        # 트레이너에게 푸쉬 알람 전송
        user = self.user_repository.get(user_id)
        trainer_fcm_token = self.trainer_fcm_token_repository.get_by_trainer_id(trainer_id)
        data = {
            'schedule_start_time': body.schedule_start_time
        }
        self.message_service.send_message(title='수업 신청', body=f'{user.user_name}님이 수업을 신청하였습니다.',
                                          token=trainer_fcm_token.fcm_token, data=data)

        return {"message": "success"}
