from app.entities.entity_trainer_availability import TrainerAvailability
from database import db


class TrainerAvailabilityRepository:
    def select_week_day_by_trainer_id(self, trainer_id):
        available_week_days = db.session.query(
            TrainerAvailability.week_day
        ).filter_by(
            trainer_id=trainer_id
        ).all()

        return available_week_days
