from flask_restx import Namespace, Resource, fields

from app.models.model_Trainer import Trainer
from database import db

ns_trainer = Namespace('trainer', description='Trainer API')

trainer_model = ns_trainer.model('Trainer', {
    'trainer_id': fields.Integer(readOnly=True, description='Trainer ID'),
    'user_id': fields.Integer(required=True, description='User ID of the Trainer'),
    'center_id': fields.Integer(description='Center ID (nullable)'),
    'trainer_pr_url': fields.String(description='Trainer Profile URL (nullable)'),
    'trainer_pt_price': fields.Integer(description='Trainer PT Price (nullable)'),
    'certification': fields.String(description='Trainer Certification (nullable)'),
    'trainer_education': fields.String(description='Trainer Education (nullable)')
})


@ns_trainer.route('')
class TrainerListResource(Resource):
    @ns_trainer.marshal_list_with(trainer_model)
    def get(self):
        # 모든 트레이너 정보 조회
        trainers = Trainer.query.all()
        return trainers

    @ns_trainer.expect(trainer_model, validate=True)
    @ns_trainer.marshal_with(trainer_model, code=201)
    def post(self):
        # 새로운 트레이너 추가
        data = ns_trainer.payload
        trainer = Trainer(
            user_id=data['user_id'],
            center_id=data.get('center_id'),
            trainer_pr_url=data.get('trainer_pr_url'),
            trainer_pt_price=data.get('trainer_pt_price'),
            certification=data.get('certification'),
            trainer_education=data.get('trainer_education')
        )
        db.session.add(trainer)
        db.session.commit()
        return trainer, 201


@ns_trainer.route('/<int:trainer_id>')
class TrainerResource(Resource):
    @ns_trainer.marshal_with(trainer_model)
    def get(self, trainer_id):
        # 특정 트레이너 정보 조회
        trainer = Trainer.query.filter_by(trainer_id=trainer_id).first()
        return trainer

    @ns_trainer.expect(trainer_model, validate=True)
    @ns_trainer.marshal_with(trainer_model)
    def put(self, trainer_id):
        # 기존 트레이너 정보 업데이트
        trainer = Trainer.query.filter_by(trainer_id=trainer_id).first()
        # todo : 레코드 없는 경우 처리
        data = ns_trainer.payload

        trainer.user_id = data['user_id']
        trainer.center_id = data.get('center_id')
        trainer.trainer_pr_url = data.get('trainer_pr_url')
        trainer.trainer_pt_price = data.get('trainer_pt_price')
        trainer.certification = data.get('certification')
        trainer.trainer_education = data.get('trainer_education')

        db.session.commit()
        return trainer
