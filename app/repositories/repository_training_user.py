from app.entities.entity_training_user import TrainingUser


class TrainingUserRepository:
    def select_by_id(self, training_user_id):
        training_user = TrainingUser.query.filter_by(training_user_id=training_user_id).first()
        return training_user
