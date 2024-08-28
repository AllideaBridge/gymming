import unittest

import boto3
from moto import mock_aws

from app import create_app
from database import db


class BaseTestCase(unittest.TestCase):
    app = None
    app_context = None

    mock_s3 = None
    s3 = None

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('test')
        cls.app.testing = True
        cls.app.debug = False
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.drop_all()
        db.create_all()
        cls.client = cls.app.test_client()

        # Moto S3 mock 시작
        cls.mock_s3 = mock_aws()
        cls.mock_s3.start()

        # 테스트용 S3 버킷 생성
        cls.s3 = boto3.client('s3', region_name='us-east-1')
        cls.s3.create_bucket(Bucket='gymming')

    def setUp(self):
        db.session.begin_nested()

    def tearDown(self):
        db.session.rollback()

    @classmethod
    def tearDownClass(cls):
        cls.mock_s3.stop()
