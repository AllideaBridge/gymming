from database import db


class Trainer(db.Model):
    trainer_id = db.Column(db.Integer, primary_key=True)
    center_id = db.Column(db.Integer, db.ForeignKey('center.center_id'), nullable=True)
    trainer_name = db.Column(db.String(20), nullable=False)
    trainer_email = db.Column(db.String(100), nullable=False)
    trainer_gender = db.Column(db.String(5), nullable=False)
    trainer_phone_number = db.Column(db.String(30), nullable=False)
    trainer_pr_url = db.Column(db.String(255), nullable=True)
    trainer_pt_price = db.Column(db.Integer, nullable=True)
    certification = db.Column(db.String(255), nullable=True)
    trainer_education = db.Column(db.String(255), nullable=True)
    trainer_login_platform = db.Column(db.String(20), nullable=True)
    lesson_name = db.Column(db.String(100), nullable=True)
    lesson_price = db.Column(db.Integer, nullable=True)
    lesson_minutes = db.Column(db.Integer, nullable=False)
    trainer_delete_flag = db.Column(db.Boolean, default=False)
