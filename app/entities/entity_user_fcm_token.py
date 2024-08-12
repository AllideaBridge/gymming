from database import db


class UserFcmToken(db.Model):
    fcm_token_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    fcm_token = db.Column(db.String(500), nullable=False)
