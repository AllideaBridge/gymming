import http
from datetime import datetime, date, timedelta

from flask import request
from flask_restx import Namespace, Resource, fields
from app.common.constants import DATETIMEFORMAT, DATEFORMAT
from app.common.exceptions import BadRequestError
from app.entities.entity_users import Users
from app.entities.entity_trainer import Trainer
from app.entities.entity_training_user import TrainingUser
from app.entities.entity_trainer_availability import TrainerAvailability
from app.entities.entity_schedule import Schedule
from app.routes.models.model_schedule import request_get_schedules_model
from app.services.service_schedule import ScheduleService
from database import db

ns_schedule = Namespace('schedules', description='Schedules related operations', path='/schedules')

# API 모델 정의
user_schedule_model = ns_schedule.model('UserSchedule', {
    'trainer_name': fields.String,
    'lesson_name': fields.String,
    'center_name': fields.String,
    'center_location': fields.String,
    'schedule_start_time': fields.DateTime,
    'schedule_id': fields.Integer
})


@ns_schedule.route('/<int:schedule_id>')
class ScheduleResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule_service = ScheduleService()

    def get(self, schedule_id):
        return self.schedule_service.get_schedule_details(schedule_id)

    def put(self, schedule_id):
        start_time = datetime.strptime(request.json['start_time'], DATETIMEFORMAT)
        status = request.json['status']

        return self.schedule_service.handle_change_user_schedule(schedule_id, start_time, status)

    def delete(self, schedule_id):
        return self.schedule_service.delete_schedule(schedule_id)


@ns_schedule.route('/user/<int:user_id>')
class UserSchedule(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule_service = ScheduleService()

    def get(self, user_id):
        date_str = request.args.get('date')
        schedule_type = request.args.get('type').upper()

        return self.schedule_service.handle_get_user_schedule(user_id, date_str, schedule_type)


@ns_schedule.route('/user/<int:schedule_id>/check-change')
class UserScheduleCheck(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule_service = ScheduleService()

    def get(self, schedule_id):
        return self.schedule_service.validate_schedule_change(schedule_id)


@ns_schedule.route('/trainer/<int:trainer_id>')
class TrainerSchedule(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule_service = ScheduleService()

    def get(self, trainer_id):
        date_str = request.args.get('date')
        schedule_date = datetime.strptime(date_str, DATEFORMAT).date()
        schedule_type = request.args.get('type').upper()
        return self.schedule_service.handle_get_trainer_schedule(trainer_id=trainer_id, date=schedule_date,
                                                                 type=schedule_type)


@ns_schedule.route('/trainer/<int:trainer_id>/users/<int:user_id>')
class TrainerAssignedUserSchedule(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule_service = ScheduleService()

    def get(self, trainer_id, user_id):
        date_str = request.args.get('date')
        schedule_date = datetime.strptime(date_str, DATEFORMAT).date()
        query_type = request.args.get('type').upper()

        result = self.schedule_service.get_training_user_schedule(trainer_id, user_id, schedule_date, query_type)
        return {"result": result}


# # 회원의 한달 중 스케쥴이 있는 날짜 조회.
# @ns_schedule.route('/<int:user_id>/<int:year>/<int:month>')
# class UserMonthScheduleList(Resource):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.schedule_service = ScheduleService()
#
#     @ns_schedule.doc(description='회원의 한달 중 스케쥴이 있는 날짜를 조회합니다.',
#                      params={
#                          'user_id': '유저 id',
#                          'year': '년도',
#                          'month': '월'
#                      })
#     def get(self, user_id, year, month):
#         scheduled_dates = self.schedule_service.get_user_month_schedule_date(user_id, year, month)
#
#         return {'dates': scheduled_dates}


# @ns_schedule.route('/<int:user_id>/<int:year>/<int:month>/<int:day>')
# class UserDayScheduleList(Resource):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.schedule_service = ScheduleService()
#
#     @ns_schedule.marshal_with(user_schedule_model)
#     @ns_schedule.doc(description='회원의 해당 날의 스케쥴 리스트 조회.',
#                      params={
#                          'user_id': '유저 id',
#                          'year': '년도',
#                          'month': '월',
#                          'day': '일'
#                      })
#     def get(self, user_id, year, month, day):
#         schedules = self.schedule_service.get_user_day_schedule(user_id, year, month, day)
#
#         return schedules


schedule_change_model = ns_schedule.model('ScheduleChangeModel', {
    # 'schedule_id': fields.Integer(required=True, description='스케쥴 id'),
    'request_time': fields.String(required=True, description='변경 시간')
})


# todo: 스케쥴 조회시 스케쥴 상태 조건 추가

# @ns_schedule.route('/<int:schedule_id>/change')
# class ScheduleChangeResource(Resource):
#     @ns_schedule.expect(schedule_change_model)
#     @ns_schedule.doc(description='스케쥴 변경 가능 기간인 경우 스케쥴 변경 api',
#                      params={
#                          'schedule_id': '스케쥴 id',
#                          'request_time': '2024-01-10 12:30:00(%Y-%m-%d %H:%M:%S)'
#                      })
#     def post(self, schedule_id):
#         body = ns_schedule.payload
#         request_time_str = body['request_time']
#
#         try:
#             request_time = datetime.strptime(request_time_str, DATETIMEFORMAT)
#         except ValueError as e:
#             logging.log(logging.ERROR, e)
#             return {'error': 'Invalid date format'}, 400
#
#         try:
#             # 트랜잭션 시작
#             with db.session.begin_nested():
#                 # 스케줄 상태 업데이트
#                 schedule = Schedule.find_by_id(schedule_id)
#                 if not schedule:
#                     return {'error': 'Schedule not found'}, 404
#
#                 training_user = TrainingUser.find_by_id(schedule.training_user_id)
#                 trainer_id = training_user.trainer_id
#
#                 conflict_schedule = Trainer.conflict_trainer_schedule(trainer_id, request_time)
#
#                 if conflict_schedule:
#                     # 충돌하는 스케줄이 있는 경우
#                     return {'message': 'New schedule conflicts with existing schedules of the trainer'}, 400
#
#
#                 schedule.schedule_status = SCHEDULE_MODIFIED
#                 db.session.add(schedule)
#
#                 new_schedule = Schedule(
#                     training_user_id=schedule.training_user_id,
#                     schedule_start_time=request_time,
#                     schedule_status=SCHEDULE_SCHEDULED  # 새 스케줄의 상태를 'scheduled'로 설정
#                 )
#                 db.session.add(new_schedule)
#
#                 # 트랜잭션 커밋
#                 db.session.commit()
#
#             return {'message': 'Schedule updated successfully'}, 200
#         except Exception as e:
#             db.session.rollback()
#             logging.log(logging.ERROR, str(e))
#             return {'error': str(e)}, 500


# @ns_schedule.route('/<int:schedule_id>/cancel')
# class ScheduleCancelResource(Resource):
#     @ns_schedule.doc(description='스케쥴 변경 가능 기간인 경우 스케쥴 취소 api',
#                      params={
#                          'schedule_id': '스케쥴 id',
#                      })
#     def post(self, schedule_id):
#         schedule = Schedule.query.filter_by(schedule_id=schedule_id).first()
#         if not schedule:
#             return {'error': 'Schedule not found'}, 404
#
#         schedule.schedule_status = SCHEDULE_CANCELLED
#         db.session.add(schedule)
#         db.session.commit()
#         return {'message': 'Schedule cancel successfully'}, 200


# 입력 받은 year, month중 트레이너의 근무 스케쥴이 꽉 차지 않은 날짜 배열을 리턴한다.
@ns_schedule.route('/trainer/<int:trainer_id>/<int:year>/<int:month>')
class TrainerMonthSchedule(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule_service = ScheduleService()

    @ns_schedule.doc(description='트레이너의 스케쥴 조정이 가능한 날을 리턴한다.',
                     params={
                         'trainer_id': '트레이너 id',
                         'year': '년',
                         'month': '월'
                     })
    def get(self, trainer_id, year, month):
        available_dates = self.schedule_service.get_available_trainer_month_schedule(trainer_id, year, month)
        return available_dates


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


@ns_schedule.route('/{schedule_id}')
class ScheduleController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule_service = ScheduleService()

    def get(self, schedule_id):
        pass


request_get_schedules = ns_schedule.model('RequestGetSchedules', request_get_schedules_model)


@ns_schedule.route('')
class SchedulesController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule_service = ScheduleService()

    @ns_schedule.expect(request_get_schedules)
    def get(self):
        params = {
            'training_user_id': request.args.get('training_user_id', type=int),
            'trainer_id': request.args.get('trainer_id', type=int),
            'user_id': request.args.get('user_id', type=int),
            'year': request.args.get('year', type=int),
            'month': request.args.get('month', type=int),
            'day': request.args.get('day', type=int),
            'week': request.args.get('week'),
            'possible': request.args.get('possible'),
            'page': request.args.get('page', type=int),
            'per_page': request.args.get('per_page', type=int)
        }

        response = self.schedule_service.handle_request(params)
        return response, http.HTTPStatus.OK
