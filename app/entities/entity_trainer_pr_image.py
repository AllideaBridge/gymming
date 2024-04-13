from database import db


class TrainerPrImage(db.Model):
    trainer_pr_image_id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'), nullable=False)
    trainer_pr_image_url = db.Column(db.String(255), nullable=False)
