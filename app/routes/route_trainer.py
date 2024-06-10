from datetime import datetime

from flask import request
from flask_restx import Namespace, Resource, fields

from app.common.constants import DATETIMEFORMAT, DATEFORMAT
from app.entities.entity_center import Center
from app.entities.entity_trainer import Trainer
from app.entities.entity_users import Users
from app.entities.entity_schedule import Schedule
from app.entities.entity_trainer_user import TrainerUser
from database import db

ns_trainer = Namespace('trainer', description='Trainer API')

# todo : 트레이너 상세조회시 엔터티 필드 최신화
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


trainer_user_model = ns_trainer.model('TrainingUser', {
    'trainer_id': fields.Integer(required=True, description='트레이너 ID'),
    'user_name': fields.String(required=True, description='사용자 이름'),
    'user_phone_number': fields.String(required=True, description='사용자 전화번호'),
    'lesson_total_count': fields.Integer(required=True, description='총 수업 횟수'),
    'exercise_days': fields.String(description='운동 일정'),
    'special_notes': fields.String(description='특별 사항')
})


@ns_trainer.route('/trainer-user')
class TrainingUserList(Resource):
    def get(self):
        # 쿼리 파라미터에서 입력값을 가져옵니다.
        trainer_id = request.args.get('trainer_id', type=int)  # 쿼리 파라미터가 없으면 None을 반환합니다.
        trainer_user_delete_flag_str = request.args.get('trainer_user_delete_flag', default='false').lower()
        trainer_user_delete_flag = trainer_user_delete_flag_str in ['true', '1']

        # 입력값 검증
        if trainer_id is None:
            return {'message': 'trainer_id는 필수입니다.'}, 400

        # TrainingUser와 Users 테이블을 조인하고, 조건에 맞는 레코드를 조회합니다.
        trainer_users = (db.session.query(TrainerUser, Users.user_name)
                          .join(Users, TrainerUser.user_id == Users.user_id)
                          .filter(TrainerUser.trainer_id == trainer_id,
                                  TrainerUser.trainer_user_delete_flag == trainer_user_delete_flag)
                          .all())

        # 조회된 레코드와 user_name을 json 형식으로 변환하여 리턴합니다.
        return [{
            'trainer_user_id': tu.trainer_user_id,
            'user_id': tu.user_id,
            'user_name': un,  # 여기서 un은 조인된 Users 테이블의 user_name입니다.
            'lesson_total_count': tu.lesson_total_count,
            'lesson_current_count': tu.lesson_current_count,
            'exercise_days': tu.exercise_days,
            'special_notes': tu.special_notes,
            'created_at': tu.created_at.strftime(DATETIMEFORMAT),
            'deleted_at': tu.deleted_at.strftime(DATETIMEFORMAT) if tu.deleted_at else ""
        } for tu, un in trainer_users], 200


@ns_trainer.route('/trainer-user/user')
class TrainingUserUser(Resource):
    @ns_trainer.expect(trainer_user_model)
    @ns_trainer.doc(description='트레이너가 회원을 추가하는 api',
                          params={
                          })
    def post(self):
        data = ns_trainer.payload
        user = Users.query.filter_by(user_name=data['user_name'], user_phone_number=data['user_phone_number']).first()

        if not user:
            return {'message': '유저가 존재하지 않습니다.'}, 404

        trainer_user = TrainerUser(
            trainer_id=data['trainer_id'],
            user_id=user.user_id,
            lesson_total_count=data['lesson_total_count'],
            lesson_current_count=0,
            exercise_days=data['exercise_days'],
            special_notes=data['special_notes']
        )

        db.session.add(trainer_user)
        db.session.commit()

        return {'message': '새로운 회원이 등록되었습니다.'}, 200

    @ns_trainer.doc(description='트레이너가 회원의 pt 횟수를 수정하는 api',
                          params={
                          })
    def put(self):
        data = ns_trainer.payload
        trainer_user_id = data['trainer_user_id']
        lesson_total_count = data['lesson_total_count']
        lesson_current_count = data['lesson_current_count']

        trainer_user = TrainerUser.query.filter_by(trainer_user_id=trainer_user_id).first()

        if trainer_user:
            # 레코드의 lesson_total_count, lesson_current_count 업데이트
            trainer_user.lesson_total_count = lesson_total_count
            trainer_user.lesson_current_count = lesson_current_count

            # 데이터베이스 세션을 통해 변경 사항 커밋
            db.session.commit()

            return {'message': 'TrainingUser updated successfully'}, 200
        else:
            return {'message': 'TrainingUser not found'}, 404

    @ns_trainer.doc(description='트레이너가 회원을 삭제하는 api',
                          params={
                          })
    def delete(self):
        data = ns_trainer.payload
        trainer_user_id = data['trainer_user_id']

        trainer_user = TrainerUser.query.filter_by(trainer_user_id=trainer_user_id).first()

        if trainer_user:
            # 레코드의 lesson_total_count, lesson_current_count 업데이트
            trainer_user.trainer_user_delete_flag = True

            # 데이터베이스 세션을 통해 변경 사항 커밋
            db.session.commit()

            return {'message': 'TrainingUser updated successfully'}, 200
        else:
            return {'message': 'TrainingUser not found'}, 404


@ns_trainer.route('/trainer-user/month-schedules')
class TrainingUserSchedules(Resource):
    @ns_trainer.doc(description='트레이너가 회원을 조회한 화면에서 해당 회원의 한달 수업 내역을 조회 하는 api ',
                          params={
                          })
    def get(self):
        trainer_user_id = request.args.get('trainer_user_id', type=int)
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)

        if not trainer_user_id:
            return {"message": "trainer_user_id는 필수 입력값이며, 정수여야 합니다."}, 400
        if not year or year < 1:
            return {"message": "year는 필수 입력값이며, 양의 정수여야 합니다."}, 400
        if not month or month < 1 or month > 12:
            return {"message": "month는 필수 입력값이며, 1부터 12 사이의 정수여야 합니다."}, 400

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        schedules = Schedule.query.filter(
            Schedule.trainer_user_id == trainer_user_id,
            Schedule.schedule_start_time >= start_date,
            Schedule.schedule_start_time < end_date
        ).all()

        return {
            "schedules": [
                {"schedule_id": schedule.schedule_id, "day": schedule.schedule_start_time.day}
                for schedule in schedules
            ]
        }


@ns_trainer.route('/trainer-user/schedule/<int:schedule_id>')
class TrainingUserSchedule(Resource):
    @ns_trainer.doc(description='트레이너가 회원을 조회한 화면에서 수업 했던 날짜를 클릭하여 해당 수업의 상세내용을 조회하는 api ',
                          params={
                          })
    def get(self, schedule_id):
        result = db.session.query(
            Schedule.schedule_start_time,
            Schedule.schedule_status,
            Center.center_location,
            Center.center_name
        ).join(TrainerUser, TrainerUser.trainer_user_id == Schedule.trainer_user_id
               ).join(Trainer, Trainer.trainer_id == TrainerUser.trainer_id
                      ).outerjoin(Center, Center.center_id == Trainer.center_id  # outerjoin 사용
                                  ).filter(Schedule.schedule_id == schedule_id).first()

        if not result:
            return {"message": "해당 schedule_id를 가진 스케줄이 존재하지 않습니다."}, 404

        schedule_start_time, schedule_status, center_location, center_name = result

        # Center 정보가 없는 경우 None 또는 적절한 대체 값을 반환
        return {
            "schedule_start_time": schedule_start_time.strftime(DATEFORMAT) if schedule_start_time else None,
            "schedule_status": schedule_status,
            "center_location": center_location if center_location else "정보 없음",
            "center_name": center_name if center_name else "정보 없음"
        }


