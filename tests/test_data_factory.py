import uuid

from app import db, Trainer, Users, TrainerUser, Schedule, ChangeTicket
from datetime import datetime, timedelta


class TestDataFactory:
    @staticmethod
    def create_trainer(trainer_social_id=uuid.uuid4().hex, name="Test Trainer", email="test@example.com", **kwargs):
        trainer = Trainer(
            trainer_social_id=trainer_social_id,
            trainer_name=name,
            trainer_phone_number=kwargs.get('phone', '010-0000-0000'),
            trainer_gender=kwargs.get('gender', 'M'),
            trainer_birthday=kwargs.get('trainer_birthday', datetime.now().date()),
            description=kwargs.get('description', 'description'),
            lesson_name=kwargs.get('lesson_name', 'lesson_name'),
            lesson_price=kwargs.get('lesson_price', 10000),
            lesson_minutes=kwargs.get('lesson_minutes', 60),
            lesson_change_range=kwargs.get('lesson_change_range', 3),
            trainer_email=email,
            center_name=kwargs.get('center_name', 'Center'),
            center_location=kwargs.get('center_location', 'center_location'),
            center_number=kwargs.get('center_number', '02-555-5555'),
            center_type=kwargs.get('center_type', '필라테스')
        )
        db.session.add(trainer)
        db.session.commit()
        return trainer

    @staticmethod
    def create_user(user_social_id=uuid.uuid4().hex, name="Test User", email="user@example.com", **kwargs):
        user = Users(
            user_social_id=user_social_id,
            user_email=email,
            user_name=name,
            user_gender=kwargs.get('gender', 'M'),
            user_phone_number=kwargs.get('phone', '010-1234-5678'),
            user_profile_img_url=kwargs.get('profile_img', 'http://example.com/profile.jpg'),
            user_birthday=kwargs.get('user_birthday', datetime.now().date())
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def create_trainer_user(trainer=None, user=None, **kwargs):
        if trainer is None:
            trainer = TestDataFactory.create_trainer()
        if user is None:
            user = TestDataFactory.create_user()

        trainer_user = TrainerUser(trainer_id=trainer.trainer_id, user_id=user.user_id)
        db.session.add(trainer_user)
        db.session.commit()
        return trainer_user

    @staticmethod
    def create_schedule(trainer_user=None, start_time=None, **kwargs):
        if trainer_user is None:
            trainer_user = TestDataFactory.create_trainer_user()
        if start_time is None:
            start_time = datetime.now() + timedelta(days=1)

        schedule = Schedule(
            trainer_user_id=trainer_user.trainer_user_id,
            schedule_start_time=start_time,
            schedule_status=kwargs.get('schedule_status', 'schedule_status')
        )
        db.session.add(schedule)
        db.session.commit()
        return schedule

    @staticmethod
    def create_change_ticket(schedule=None, **kwargs):
        if schedule is None:
            schedule = TestDataFactory.create_schedule()

        change_ticket = ChangeTicket(
            schedule_id=schedule.schedule_id,
            change_from=kwargs.get('change_from', 'change_from'),
            change_type=kwargs.get('change_type', 'change_type'),
            description=kwargs.get('description', 'description'),
            status=kwargs.get('status', 'status'),
            request_time=kwargs.get('request_time', datetime.now())
        )

        db.session.add(change_ticket)
        db.session.commit()
        return change_ticket

    @staticmethod
    def create_trainer_with_users(user_count=3):
        trainer = TestDataFactory.create_trainer()
        users = [TestDataFactory.create_user(f"User {i}") for i in range(user_count)]
        trainer_users = [TestDataFactory.create_trainer_user(trainer, user) for user in users]
        return trainer, users, trainer_users

    @staticmethod
    def create_trainer_user_with_schedules(schedule_count=5):
        trainer_user = TestDataFactory.create_trainer_user()
        start_time = datetime.now() + timedelta(days=1)
        schedules = [
            TestDataFactory.create_schedule(trainer_user, start_time + timedelta(days=i))
            for i in range(schedule_count)
        ]
        return trainer_user, schedules


class ScheduleBuilder:
    def __init__(self):
        self.trainer = None
        self.user = None
        self.trainer_user = None
        self.start_time = datetime.now() + timedelta(days=1)
        self.status = 'SCHEDULED'

    def with_trainer(self, trainer=None):
        self.trainer = trainer or TestDataFactory.create_trainer()
        return self

    def with_user(self, user=None):
        self.user = user or TestDataFactory.create_user()
        return self

    def with_trainer_user(self, trainer_user=None):
        self.trainer_user = trainer_user or TestDataFactory.create_trainer_user(self.trainer, self.user)
        return self

    def with_start_time(self, start_time):
        self.start_time = start_time
        return self

    def with_status(self, status):
        self.status = status
        return self

    def build(self):
        if not self.trainer_user:
            self.trainer_user = TestDataFactory.create_trainer_user(self.trainer, self.user)
        return TestDataFactory.create_schedule(self.trainer_user, self.start_time, schedule_status=self.status)


class ChangeTicketBuilder:

    def __init__(self):
        self.schedule = None
        self.trainer_user = None
        self.trainer = None
        self.user = None
        self.status = "status"

    def with_trainer(self, trainer=None):
        self.trainer = trainer or TestDataFactory.create_trainer()
        return self

    def with_user(self, user=None):
        self.user = user or TestDataFactory.create_user()
        return self

    def with_schedule(self, schedule=None):
        self.schedule = schedule or TestDataFactory.create_schedule()
        return self

    def with_trainer_user(self, trainer_user=None):
        self.trainer_user = trainer_user or TestDataFactory.create_trainer_user()
        return self

    def with_status(self, status=None):
        self.status = status
        return self

    def build(self):
        if self.schedule is None:
            self.schedule = (ScheduleBuilder()
                             .with_user(self.user)
                             .with_trainer(self.trainer)
                             .with_trainer_user(self.trainer_user)
                             .build())
        return TestDataFactory.create_change_ticket(self.schedule, status=self.status)
