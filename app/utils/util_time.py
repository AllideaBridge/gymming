from datetime import datetime, timedelta


def calculate_lesson_slots(start_time, end_time, lesson_minutes):
    start_time = datetime.combine(datetime.today(), start_time)
    end_time = datetime.combine(datetime.today(), end_time)

    duration = end_time - start_time
    lesson_duration = timedelta(minutes=lesson_minutes)
    slots = duration // lesson_duration

    return slots
