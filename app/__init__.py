import logging

from flask import Flask
from flask_restx import Api

from database import db
from app.routes.route_training_user import ns_training_user
from app.routes.route_users import ns_user
from app.routes.route_schedule import ns_schedule
from app.routes.route_trainer import ns_trainer
from app.routes.route_request import ns_request
from app.models.model_Center import Center
from app.models.model_CenterPrImage import CenterPrImage
from app.models.model_TrainingUser import TrainingUser
from app.models.model_Request import Request
from app.models.model_Schedule import Schedule
from app.models.model_Trainer import Trainer
from app.models.model_TrainerPrImage import TrainerPrImage
from app.models.model_Users import Users
from app.models.model_TrainerAvailability import TrainerAvailability


def create_app(env):
    app = Flask(__name__)

    api = Api(app, version='1.0', title='Gymming', description='Gymming api', doc="/api-docs")
    api.add_namespace(ns_user)
    api.add_namespace(ns_trainer)
    api.add_namespace(ns_schedule)
    api.add_namespace(ns_request)
    api.add_namespace(ns_training_user)

    if env == "test":
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1111@localhost:3306/gymming_test'
    else:
        # Docker에서 실행 중인 MySQL 서버에 연결
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1111@localhost:3306/gymming'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # db 인스턴스 초기화
    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app
