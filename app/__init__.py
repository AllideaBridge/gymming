import logging
import os

import firebase_admin
from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api

from app.common.error_handlers import register_error_handlers
from app.routes.route_auth import ns_auth
from app.routes.route_image import ns_image
from database import db
from app.routes.route_users import ns_user
from app.routes.route_schedule import ns_schedule
from app.routes.route_trainer import ns_trainer
from app.routes.route_change_ticket import ns_change_ticket
from app.routes.route_trainer_user import ns_trainer_user
from app.entities.entity_trainer_user import TrainerUser
from app.entities.entity_change_ticket import ChangeTicket
from app.entities.entity_schedule import Schedule
from app.entities.entity_trainer import Trainer
from app.entities.entity_trainer_pr_image import TrainerPrImage
from app.entities.entity_users import Users
from app.entities.entity_trainer_availability import TrainerAvailability
from firebase_admin import credentials

load_dotenv()


def create_app(env):
    app = Flask(__name__)

    api = Api(app, version='1.0', title='Gymming', description='Gymming api', doc="/api-docs")
    api.add_namespace(ns_user)
    api.add_namespace(ns_trainer)
    api.add_namespace(ns_schedule)
    api.add_namespace(ns_change_ticket)
    api.add_namespace(ns_auth)
    api.add_namespace(ns_trainer_user)
    api.add_namespace(ns_image)

    if env == "test":
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1111@0.0.0.0:3306/gymming_test'
    else:
        # Firebase 초기화
        project_root = os.path.dirname(os.path.abspath(__file__))
        cred_path = os.path.join(project_root, 'gymming-firebase-adminsdk.json')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

        # Docker에서 실행 중인 MySQL 서버에 연결
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # db 인스턴스 초기화
    db.init_app(app)

    ## todo.txt : 나중에 키 설정
    app.config['JWT_SECRET_KEY'] = 'your_secret_key'

    ## todo.txt : 지우기
    # app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

    JWTManager(app)
    with app.app_context():
        db.create_all()

    register_error_handlers(app)
    return app
