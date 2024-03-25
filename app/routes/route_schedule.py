import logging
from datetime import datetime, date
from calendar import monthrange

from flask_restx import Namespace, Resource, fields
from sqlalchemy import func
from sqlalchemy.sql.functions import coalesce

from app.common.Constants import SCHEDULE_CANCELLED, SCHEDULE_SCHEDULED, DATETIMEFORMAT, DATEFORMAT
from app.models.model_Users import Users
from app.models.model_Trainer import Trainer
from app.models.model_Center import Center
from app.models.model_TrainingUser import TrainingUser
from app.models.model_TrainerAvailability import TrainerAvailability
from app.models.model_Schedule import Schedule
from database import db

ns_schedule = Namespace('schedules', description='Schedules related operations')

# API 모델 정의
user_schedule_model = ns_schedule.model('UserSchedule', {
    'trainer_name': fields.String,
    'lesson_name': fields.String,
    'center_name': fields.String,
    'center_location': fields.String,
    'schedule_start_time': fields.DateTime,
    'schedule_id': fields.Integer
})


# 회원의 한달 중 스케쥴이 있는 날짜 조회.
@ns_schedule.route('/<int:user_id>/<int:year>/<int:month>')
class UserMonthScheduleList(Resource):
    @ns_schedule.doc(description='회원의 한달 중 스케쥴이 있는 날짜를 조회합니다.',
                     params={
                         'user_id': '유저 id',
                         'year': '년도',
                         'month': '월'
                     })
    def get(self, user_id, year, month):
        schedules = db.session.query(func.distinct(func.date(Schedule.schedule_start_time))).join(TrainingUser).filter(
            TrainingUser.user_id == user_id,
            db.extract('year', Schedule.schedule_start_time) == year,
            db.extract('month', Schedule.schedule_start_time) == month).all()

        scheduled_dates = [schedule[0].strftime(DATEFORMAT) for schedule in schedules]

        return {'dates': sorted(scheduled_dates)}


@ns_schedule.route('/<int:user_id>/<int:year>/<int:month>/<int:day>')
class UserDayScheduleList(Resource):
    @ns_schedule.marshal_with(user_schedule_model)
    @ns_schedule.doc(description='회원의 해당 날의 스케쥴 리스트 조회.',
                     params={
                         'user_id': '유저 id',
                         'year': '년도',
                         'month': '월',
                         'day': '일'
                     })
    def get(self, user_id, year, month, day):
        schedules = db.session.query(
            Trainer.trainer_name,
            coalesce(Trainer.lesson_name, '').label('lesson_name'),
            coalesce(Center.center_name, '').label('center_name'),
            coalesce(Center.center_location, '').label('center_location'),
            Schedule.schedule_start_time,
            Schedule.schedule_id
        ).join(TrainingUser, TrainingUser.training_user_id == Schedule.training_user_id) \
            .join(Trainer, TrainingUser.trainer_id == Trainer.trainer_id) \
            .outerjoin(Center, Trainer.center_id == Center.center_id) \
            .filter(TrainingUser.user_id == user_id,
                    func.year(Schedule.schedule_start_time) == year,
                    func.month(Schedule.schedule_start_time) == month,
                    func.day(Schedule.schedule_start_time) == day) \
            .all()

        return schedules


# todo: 스케쥴 조회시 스케쥴 상태 조건 추가

@ns_schedule.route('/<int:schedule_id>/change')
class ScheduleChangeResource(Resource):
    @ns_schedule.doc(description='스케쥴 변경 가능 기간인 경우 스케쥴 변경 api',
                     params={
                         'schedule_id': '스케쥴 id',
                         'request_time': '2024-01-10 12:30:00(%Y-%m-%d %H:%M:%S)'
                     })
    def post(self, schedule_id):
        body = ns_schedule.payload
        request_time_str = body['request_time']

        try:
            request_time = datetime.strptime(request_time_str, DATETIMEFORMAT)
        except ValueError as e:
            logging.log(logging.ERROR, e)
            return {'error': 'Invalid date format'}, 400

        try:
            # 트랜잭션 시작
            with db.session.begin_nested():
                # 스케줄 상태 업데이트
                schedule = Schedule.find_by_id(schedule_id)
                if not schedule:
                    return {'error': 'Schedule not found'}, 404

                training_user = TrainingUser.find_by_id(schedule.training_user_id)
                trainer_id = training_user.trainer_id

                conflict_schedule = Trainer.conflict_trainer_schedule(trainer_id, request_time)

                if conflict_schedule:
                    # 충돌하는 스케줄이 있는 경우
                    return {'message': 'New schedule conflicts with existing schedules of the trainer'}, 400

                schedule.schedule_status = SCHEDULE_CANCELLED
                db.session.add(schedule)

                new_schedule = Schedule(
                    training_user_id=schedule.training_user_id,
                    schedule_start_time=request_time,
                    schedule_status=SCHEDULE_SCHEDULED  # 새 스케줄의 상태를 'scheduled'로 설정
                )
                db.session.add(new_schedule)

                # 트랜잭션 커밋
                db.session.commit()

            return {'message': 'Schedule updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            logging.log(logging.ERROR, str(e))
            return {'error': str(e)}, 500


@ns_schedule.route('/<int:schedule_id>/cancel')
class ScheduleCancelResource(Resource):
    @ns_schedule.doc(description='스케쥴 변경 가능 기간인 경우 스케쥴 취소 api',
                     params={
                         'schedule_id': '스케쥴 id',
                     })
    def post(self, schedule_id):
        schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
        if not schedule:
            return {'error': 'Schedule not found'}, 404

        schedule.schedule_status = SCHEDULE_CANCELLED
        db.session.add(schedule)
        db.session.commit()
        return {'message': 'Schedule cancel successfully'}, 200


# 입력 받은 year, month중 트레이너의 근무 스케쥴이 꽉 차지 않은 날짜 배열을 리턴한다.
@ns_schedule.route('/trainer/<int:trainer_id>/<int:year>/<int:month>')
class TrainerMonthSchedule(Resource):
    @ns_schedule.doc(description='트레이너의 스케쥴 조정이 가능한 날을 리턴한다.',
                     params={
                         'trainer_id': '트레이너 id',
                         'year': '년',
                         'month': '월'
                     })
    def get(self, trainer_id, year, month):
        # 1단계: 트레이너의 전체 가능 요일 조회
        available_week_days = db.session.query(
            TrainerAvailability.week_day
        ).filter_by(
            trainer_id=trainer_id
        ).all()

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
        occupied_dates = db.session.query(
            func.date(Schedule.schedule_start_time).label('date')
        ).join(TrainingUser, TrainingUser.training_user_id == Schedule.training_user_id
               ).join(Trainer, Trainer.trainer_id == TrainingUser.trainer_id
                      ).join(TrainerAvailability, db.and_(
            Trainer.trainer_id == TrainerAvailability.trainer_id,
            func.weekday(Schedule.schedule_start_time) == TrainerAvailability.week_day
        )).filter(
            Trainer.trainer_id == trainer_id,
            func.year(Schedule.schedule_start_time) == year,
            func.month(Schedule.schedule_start_time) == month
        ).group_by(
            func.date(Schedule.schedule_start_time)
        ).having(
            func.max(TrainerAvailability.possible_lesson_cnt) <= func.count()
        ).all()

        for date, in occupied_dates:
            available_dates.discard(date.strftime(DATEFORMAT))

        # "근무 가능 날짜" 목록에서 조건을 충족하는 날짜를 제외한 결과 반환
        return sorted(list(available_dates))


@ns_schedule.route('/trainer/<int:trainer_id>/<int:year>/<int:month>/<int:day>')
class TrainerDaySchedule(Resource):
    @ns_schedule.doc(description='트레이너의 하루 스케쥴 리스트를 리턴한다.',
                     params={
                         'trainer_id': '트레이너 id',
                         'year': '년',
                         'month': '월',
                         'day': '일'
                     })
    def get(self, trainer_id, year, month, day):
        date_filter = date(year, month, day)

        trainer_details = db.session.query(
            Trainer.lesson_minutes,
            Trainer.lesson_change_range,
            TrainerAvailability.start_time,
            TrainerAvailability.end_time,
        ) \
            .join(TrainerAvailability, (TrainerAvailability.trainer_id == Trainer.trainer_id) \
                  & (TrainerAvailability.week_day == date_filter.weekday())) \
            .filter(Trainer.trainer_id == trainer_id,
                    Trainer.trainer_delete_flag == False) \
            .first()  # 가정: 모든 스케줄에 대해 lesson_minutes와 availability_start_time는 동일

        if trainer_details:
            formatted_start_time = trainer_details.start_time.strftime(
                "%H:%M") if trainer_details.start_time else None
            formatted_end_time = trainer_details.end_time.strftime(
                "%H:%M") if trainer_details.end_time else None

            result = {
                'lesson_minutes': trainer_details.lesson_minutes,
                'lesson_change_range': trainer_details.lesson_change_range,
                'availability_start_time': formatted_start_time,
                'availability_end_time': formatted_end_time
            }
        else:
            result = {}

        schedules = db.session.query(
            Schedule.schedule_id,
            Schedule.schedule_start_time
        ) \
            .join(TrainingUser, (TrainingUser.training_user_id == Schedule.training_user_id) \
                  & (TrainingUser.training_user_delete_flag == False) \
                  & (Schedule.schedule_delete_flag == False) \
                  & (db.func.date(Schedule.schedule_start_time) == date_filter)) \
            .join(Trainer, (Trainer.trainer_id == TrainingUser.trainer_id) \
                  & (Trainer.trainer_id == trainer_id) \
                  & (Trainer.trainer_delete_flag == False)) \
            .all()

        # todo : 스케쥴 정렬 조건 추가하기.
        result['schedules'] = [{
            'schedule_id': schedule.schedule_id,
            'schedule_start_time': schedule.schedule_start_time.strftime(DATETIMEFORMAT)
        } for schedule in schedules]

        return result


# todo: 스케쥴 조회시 스케쥴 상태 조건 추가


@ns_schedule.route('/trainer/<int:trainer_id>/<int:year>/<int:month>/<int:day>/week')
class TrainerWeekSchedule(Resource):
    @ns_schedule.doc(description='트레이너의 일주일 스케쥴 리스트를 리턴한다.',
                     params={
                         'trainer_id': '트레이너 id',
                         'year': '년',
                         'month': '월',
                         'day': '일'
                     })
    def get(self, trainer_id, year, month, day):
        start_date = date(year, month, day)
        end_date = date(year, month, day + 7)

        results = db.session.query(Users.user_id, Users.user_name, Schedule.schedule_start_time) \
            .join(TrainingUser,
                  (TrainingUser.training_user_id == Schedule.training_user_id) \
                  & (TrainingUser.trainer_id == trainer_id) \
                  & (db.func.date(Schedule.schedule_start_time) >= start_date) \
                  & (db.func.date(Schedule.schedule_start_time) <= end_date)) \
            .join(Trainer, Trainer.trainer_id == TrainingUser.trainer_id) \
            .join(Users, Users.user_id == TrainingUser.user_id) \
            .all()

        return [{'user_id': r[0], 'user_name': r[1], 'schedule_start_time': r[2].strftime(DATETIMEFORMAT)}
                for r in results]
