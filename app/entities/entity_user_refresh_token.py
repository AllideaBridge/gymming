from database import db


class UserRefreshToken(db.Model):
    refresh_token_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    refresh_token = db.Column(db.String(500), nullable=False)
