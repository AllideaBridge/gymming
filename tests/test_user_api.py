import unittest
from app import create_app
from database import db
from tests.test_data_factory import TestDataFactory


class UserTestCase(unittest.TestCase):
    app = None
    app_context = None

    @classmethod
    def setUpClass(cls):
        cls.app = create_app('test')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.drop_all()
        db.create_all()
        cls.client = cls.app.test_client()

    def setUp(self):
        db.session.begin_nested()

    def tearDown(self):
        db.session.rollback()

    def test_유저_이름과_핸드폰번호로_조회(self):
        user_name = "ty"
        user_phone_number = "010-0001-5746"
        TestDataFactory.create_user(name=user_name, phone=user_phone_number)
        response = self.client.get(f'/users/check?user_name={user_name}&user_phone_number={user_phone_number}')

        self.assertEqual(response.status_code, 200)
        print(response.get_json())
