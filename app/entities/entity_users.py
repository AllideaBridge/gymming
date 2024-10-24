from sqlalchemy import event

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


# 이벤트 리스너 설정
@event.listens_for(Users.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    db.session.add_all([
        Users(user_social_id='user_for_lock')
    ])
    db.session.commit()
