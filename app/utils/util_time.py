from datetime import datetime, timedelta

from app.common.constants import DATETIMEFORMAT
from app.common.exceptions import BadRequestError


def calculate_lesson_slots(start_time, end_time, lesson_minutes):
    start_time = datetime.combine(datetime.today(), start_time)
    end_time = datetime.combine(datetime.today(), end_time)

    duration = end_time - start_time
    lesson_duration = timedelta(minutes=lesson_minutes)
    slots = duration // lesson_duration

    return slots


def validate_datetime(start_time):
    date_time = datetime.strptime(start_time, DATETIMEFORMAT)
    if date_time < datetime.now():
        raise BadRequestError('datetime must be in the future.')
    return start_time
