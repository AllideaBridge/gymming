from database import db


class TrainerRefreshToken(db.Model):
    refresh_token_id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.trainer_id'), nullable=False)
    refresh_token = db.Column(db.String(500), nullable=False)
