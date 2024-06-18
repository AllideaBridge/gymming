from database import db


class Center(db.Model):
    center_id = db.Column(db.Integer, primary_key=True)
    center_name = db.Column(db.String(30), nullable=True)
    center_location = db.Column(db.String(100), nullable=True)
    center_number = db.Column(db.String(20), nullable=True)
    center_type = db.Column(db.String(20), nullable=True)
    center_delete_flag = db.Column(db.Boolean, default=False)
