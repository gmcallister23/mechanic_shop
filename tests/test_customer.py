from app import create_app
from app.models import db
import unittest

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        self.client = self.app.test_client()
    
    def test_create_member(self):
        customer_payload = {
            "name": "John Doe",
            "email": "john@test.com",
            "phone": "1234567899",
            "password": "john"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")