from database import db


class TrainerFcmToken(db.Model):
    fcm_token_id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'), nullable=False)
    fcm_token = db.Column(db.String(500), nullable=False)
