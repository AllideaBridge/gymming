from database import db


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_social_id = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=True)
    user_name = db.Column(db.String(20), nullable=True)
    user_gender = db.Column(db.String(5), nullable=True)
    user_phone_number = db.Column(db.String(20), nullable=True)
    user_delete_flag = db.Column(db.Boolean, default=False)
    user_birthday = db.Column(db.Date, nullable=True)
