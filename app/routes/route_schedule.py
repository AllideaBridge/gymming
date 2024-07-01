from datetime import datetime

from flask import request
from flask_restx import Namespace, Resource, fields
from app.common.constants import DATETIMEFORMAT, DATEFORMAT
from app.common.exceptions import ApplicationError
from app.services.service_schedule import ScheduleService

ns_schedule = Namespace('schedules', description='Schedules related operations', path='/schedules')


@ns_schedule.route('')
class Schedules(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schedule_service = ScheduleService()

    def post(self):
        data = request.json
        trainer_id = data.get('trainer_id')
        user_id = data.get('user_id')
        schedule_start_time = datetime.strptime(data.get('schedule_start_time'), DATETIMEFORMAT)
        try:
            result = self.schedule_service.create_schedule(trainer_id, user_id, schedule_start_time)
        except ApplicationError as e:
            return {'message': e.message}, 400

        return result


@ns_schedule.route('/<int:schedule_id>')
class Schedule(Resource):
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

        result = self.schedule_service.get_trainer_user_schedule(trainer_id, user_id, schedule_date, query_type)
        return {"result": result}
