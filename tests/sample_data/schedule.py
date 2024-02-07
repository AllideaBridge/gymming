from datetime import datetime

from app import Schedule

sample_schedule = Schedule(
    lesson_id=1,
    schedule_start_time=datetime(2024, 1, 24, 9, 0, 0),
    schedule_end_time=datetime(2024, 1, 24, 10, 0, 0),
    schedule_status='Confirmed'
)

sample_schedules = [
    Schedule(
        lesson_id=1,
        schedule_start_time=datetime(2024, 1, 24, 9, 0, 0),
        schedule_end_time=datetime(2024, 1, 24, 10, 0, 0),
        schedule_status='Confirmed'
    ),
    Schedule(
        lesson_id=1,
        schedule_start_time=datetime(2024, 1, 24, 9, 0, 0),
        schedule_end_time=datetime(2024, 1, 24, 10, 0, 0),
        schedule_status='Confirmed'
    ),
    Schedule(
        lesson_id=1,
        schedule_start_time=datetime(2024, 1, 24, 9, 0, 0),
        schedule_end_time=datetime(2024, 1, 24, 10, 0, 0),
        schedule_status='Confirmed'
    )
]
