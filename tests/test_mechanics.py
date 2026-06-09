from app import create_app
from app.models import db, Mechanic
import unittest
from app.utils.util import encode_token

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(name='test_mechanic', email='mechanic@test.com', phone='9876543210', title='test_title')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()

    def test_create_mechanic(self):
        mechanic_payload = {
            'name': 'Tom Thumb',
            'email': 'tom@test.com',
            'phone': '9876543210',
            'title': 'mechanic'
        }

        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'Tom Thumb')

    def test_invalid_create_mechanic(self):
        mechanic_payload = {
            'name': 'Tom Thumb',
            'email': 'tom@test.com', 
            'phone': '9876543210'
        }
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['title'], ['Missing data for required field.'])
    
    def test_update_mechanic(self):
        mechanic_update_payload = {
            'name' : 'Mot',
            'email': '',
            'phone': '',
            'title': ''       
        }

        response = self.client.put('/mechanics/1', json=mechanic_update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Mot')
        self.assertEqual(response.json['email'], 'mechanic@test.com')

    def test_get_all_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_mechanic')

    def test_get_mechanic_by_id(self):
        response = self.client.get('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'], 'mechanic@test.com')
    
    def test_delete_mechanic(self):
        response = self.client.delete('/mechanics/1')
        self.assertEqual(response.status_code, 200)
    
    def test_get_popular_mechanics(self):
        response = self.client.get('/mechanics/popular')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_mechanic')