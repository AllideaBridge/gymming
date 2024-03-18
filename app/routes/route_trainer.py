from flask import request
from flask_restx import Namespace, Resource, fields

from app.common.Constants import DATETIMEFORMAT
from app.models.model_Trainer import Trainer
from app.models.model_Users import Users
from app.models.model_TrainingUser import TrainingUser
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


@ns_trainer.route('/training_users')
class TrainingUserList(Resource):
    def get(self):
        # 쿼리 파라미터에서 입력값을 가져옵니다.
        trainer_id = request.args.get('trainer_id', type=int)  # 쿼리 파라미터가 없으면 None을 반환합니다.
        training_user_delete_flag_str = request.args.get('training_user_delete_flag', default='false').lower()
        training_user_delete_flag = training_user_delete_flag_str in ['true', '1']

        # 입력값 검증
        if trainer_id is None:
            return {'message': 'trainer_id는 필수입니다.'}, 400

        # TrainingUser와 Users 테이블을 조인하고, 조건에 맞는 레코드를 조회합니다.
        training_users = (db.session.query(TrainingUser, Users.user_name)
                          .join(Users, TrainingUser.user_id == Users.user_id)
                          .filter(TrainingUser.trainer_id == trainer_id,
                                  TrainingUser.training_user_delete_flag == training_user_delete_flag)
                          .all())

        # 조회된 레코드와 user_name을 json 형식으로 변환하여 리턴합니다.
        return [{
            'training_user_id': tu.training_user_id,
            'user_id': tu.user_id,
            'user_name': un,  # 여기서 un은 조인된 Users 테이블의 user_name입니다.
            'lesson_total_count': tu.lesson_total_count,
            'lesson_current_count': tu.lesson_current_count,
            'exercise_days': tu.exercise_days,
            'special_notes': tu.special_notes,
            'created_at': tu.created_at.strftime(DATETIMEFORMAT),
            'deleted_at': tu.deleted_at.strftime(DATETIMEFORMAT) if tu.deleted_at else ""
        } for tu, un in training_users], 200

# todo : 리스트 조회시 pagenation 적용.
