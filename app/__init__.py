import logging

from flask import Flask
from flask_restx import Api

from database import db
from app.routes.users import ns_user
from app.routes.schedule import ns_schedule
from app.routes.trainer import ns_trainer
from app.routes.request import ns_request
from app.models.Center import Center
from app.models.CenterPrImage import CenterPrImage
from app.models.TrainingUser import TrainingUser
from app.models.Request import Request
from app.models.Schedule import Schedule
from app.models.Trainer import Trainer
from app.models.TrainerPrImage import TrainerPrImage
from app.models.Users import Users
from app.models.TrainerAvailability import TrainerAvailability


def create_app(env):
    app = Flask(__name__)

    api = Api(app, version='1.0', title='Gymming', description='Gymming api', doc="/api-docs")
    api.add_namespace(ns_user)
    api.add_namespace(ns_trainer)
    api.add_namespace(ns_schedule)
    api.add_namespace(ns_request)

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
