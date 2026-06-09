from app import create_app
from app.models import db, Inventory
import unittest
from app.utils.util import encode_token

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        

        with self.app.app_context():
           
            db.drop_all()
            db.create_all()

            self.inventory = Inventory(part_name='test_part', price=19.90)
            db.session.add(self.inventory)
            db.session.commit()

            self.inventory_id = self.inventory.id

        self.client = self.app.test_client()

    def test_create_inventory(self):
        inventory_payload = {
            'part_name': 'belt',
            'price': '19.99'
        }

        response = self.client.post('/inventory/', json=inventory_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], 'belt')

    def test_invalid_inventory(self):
        inventory_payload = {
            'price': '19.99'
        }

        response = self.client.post('/inventory/', json=inventory_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['part_name'], ['Missing data for required field.'])

    def test_get_all_inventory(self):
        response = self.client.get('/inventory/')
        # print(response.json)
        # print('STATUS:', response.status_code)
        # print("JSON:", response.json)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['part_name'], 'test_part')

    def test_get_inventory_by_id(self):
        response = self.client.get(f'/inventory/{self.inventory_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'test_part')

    def test_update_inventory(self):
        inventory_update_payload = {
            'price': 14.99
        }

        response = self.client.put(f'/inventory/{self.inventory_id}', json=inventory_update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['price'], 14.99)

    def test_delete_inventory(self):
        response = self.client.delete(f'/inventory/{self.inventory_id}')
        self.assertEqual(response.status_code, 200)