from calendar import monthrange
from datetime import datetime

from app.common.constants import DATEFORMAT
from app.common.exceptions import BadRequestError
from app.repositories.repository_schedule import ScheduleRepository
from app.repositories.repository_trainer_availability import TrainerAvailabilityRepository


class ScheduleService:

    def __init__(self):
        self.schedule_repository = ScheduleRepository()
        self.trainer_availability_repository = TrainerAvailabilityRepository()

    def handle_request(self, params):
        if params['training_user_id']:
            return self.get_training_user_schedules(params),
        elif params['trainer_id']:
            return self.get_schedule_by_trainer(params)
        elif params['user_id']:
            return self.get_schedule_by_user(params)
        else:
            print('hii')
            raise BadRequestError

    def get_training_user_schedules(self, params):
        if params['year'] and params['month']:
            return self.get_training_user_month_schedules(params)
        raise BadRequestError

    def get_training_user_month_schedules(self, params):
        training_user_id = params['training_user_id']
        year = params['year']
        month = params['month']
        page = params['page']
        per_page = params['per_page']
        schedules = self.schedule_repository.select_schedule_day_by_tu_id_and_year_month(
            training_user_id=training_user_id, year=year, month=month, page=page, per_page=per_page)

        return {
            "schedules": [
                {"schedule_id": schedule.schedule_id, "day": schedule.schedule_start_time.day}
                for schedule in schedules
            ]
        }

    def get_user_month_schedule_date(self, user_id, year, month):
        schedules = self.schedule_repository.select_month_schedule_time_by_user_id(user_id, year, month)
        scheduled_dates = [schedule[0].strftime(DATEFORMAT) for schedule in schedules]
        return sorted(scheduled_dates)

    def get_user_day_schedule(self, user_id, year, month, day):
        schedules = self.schedule_repository.select_day_schedule_by_user_id(user_id, year, month, day)
        return schedules

    # todo : ScheduleChangeResource
    # todo : ScheduleCancelResource

    def get_available_trainer_month_schedule(self, trainer_id, year, month):
        # 1단계: 트레이너의 전체 가능 요일 조회
        available_week_days = self.trainer_availability_repository.select_week_day_by_trainer_id(trainer_id)

        if not available_week_days:
            return []

        available_week_days = set([week_day for week_day, in available_week_days])

        # 2단계: 해당 월의 모든 날짜를 순회하며 "근무 가능 날짜" 목록 생성
        available_dates = set()
        num_days = monthrange(year, month)[1]
        for day in range(1, num_days + 1):
            date = datetime(year, month, day)
            if date.weekday() in available_week_days:
                available_dates.add(date.strftime(DATEFORMAT))

        # 3단계: 조건을 충족 하는 날짜 조회 및 "근무 가능 날짜"에서 제외
        full_dates = self.schedule_repository.select_full_date_by_trainer_id_and_year_month(trainer_id, year, month)
        for date, in full_dates:
            available_dates.discard(date.strftime(DATEFORMAT))

        # "근무 가능 날짜" 목록에서 조건을 충족하는 날짜를 제외한 결과 반환
        return sorted(list(available_dates))
