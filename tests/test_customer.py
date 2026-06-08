from app import create_app
from app.models import db, Customer
import unittest
from app.utils.util import encode_token
#from datetime import datetime

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(name='test_customer', email='test@test.com', phone='1234567890', password='test')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token(1) 
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
    
    #helper function for cleaner tests --> add anywhere there are headers for auth --> see update customer for example
    def login(self):
        credentials = {
            "email": "test@test.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json=credentials)
        return response.json['token']

    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "phone": "7894756133",
            "password": "john"
        }

        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['email'], ['Missing data for required field.'])

    def test_login_customer(self):
        credentials = {
            "email": 'test@test.com',
            "password": 'test'
        }

        response = self.client.post('/customers/login', json=credentials)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertIn('token', response.json)
        #return response.json['token']
    
    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid email or password!')
    
    def test_update_customer(self):
        update_payload = {
            "name": 'Peter',
            "email": '',
            "phone": '',
            "password": ''
        }

        headers = {'Authorization': 'Bearer ' + self.login()}

        response = self.client.put('/customers/1', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Peter')
        self.assertEqual(response.json['email'], 'test@test.com')

    def test_get_all_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_customer')

    def test_delete_member(self):
        headers = {'Authorization': 'Bearer ' + self.login()}
        response = self.client.delete('/customers/1', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_get_customer_by_id(self):
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], 'test@test.com')

    