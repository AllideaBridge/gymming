from app.repositories.repository_token import TokenRepository


class TokenService:
    def __init__(self):
        self.token_repository = TokenRepository()

    def get_user_token(self, user_id):
        return self.token_repository.select_user_refresh_token_by_user_id(user_id)

    def get_trainer_token(self, trainer_id):
        return self.token_repository.select_trainer_refresh_token_by_trainer_id(trainer_id)

    def insert_user_token(self, user_id, refresh_token):
        old_token = self.token_repository.select_user_refresh_token_by_user_id(user_id)
        if old_token is None:
            return self.token_repository.insert_user_refresh_token(user_id, refresh_token)

        return self.token_repository.update(old_token, refresh_token)

    def insert_trainer_token(self, trainer_id, refresh_token):
        old_token = self.token_repository.select_trainer_refresh_token_by_trainer_id(trainer_id)
        if old_token is None:
            return self.token_repository.insert_trainer_refresh_token(trainer_id, refresh_token)

        return self.token_repository.update(old_token, refresh_token)