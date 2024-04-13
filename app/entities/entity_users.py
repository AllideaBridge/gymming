from database import db


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    user_name = db.Column(db.String(20), nullable=False)
    user_gender = db.Column(db.String(5), nullable=True)
    user_phone_number = db.Column(db.String(20), nullable=False)
    user_profile_img_url = db.Column(db.String(255), nullable=True)
    user_delete_flag = db.Column(db.Boolean, default=False)
    user_login_platform = db.Column(db.String(20), nullable=False)
    user_birthday = db.Column(db.String(20), nullable=True)
