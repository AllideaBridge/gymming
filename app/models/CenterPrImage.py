from database import db


class CenterPrImage(db.Model):
    center_pr_image_id = db.Column(db.Integer, primary_key=True)
    center_id = db.Column(db.Integer, db.ForeignKey('center.center_id'), nullable=False)
    center_pr_image_url = db.Column(db.String(255), nullable=False)
