from app.entities.entity_trainer_user import TrainerUser


class TrainerUserRepository:
    def select_by_id(self, trainer_user_id):
        trainer_user = TrainerUser.query.filter_by(trainer_user_id=trainer_user_id).first()
        return trainer_user
