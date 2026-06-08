from app import create_app
from app.models import db, Service_ticket, Customer, Inventory, Service_ticketInventory
import unittest
from datetime import datetime
#from app.utils.util import encode_token

class TestServiceTickets(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        
        with self.app.app_context():
            db.drop_all()
            db.create_all()

            self.customer = Customer(name='test_customer', email='customer@test.com', phone='1234567890', password='test')
            db.session.add(self.customer)
            db.session.commit()

            self.service_ticket = Service_ticket(vin='testvin', service_date=datetime.strptime('1900-01-01', '%Y-%m-%d').date(), service_desc='test_service', customer_id=self.customer.id)
        
            db.session.add(self.service_ticket)
            db.session.commit()

            self.inventory = Inventory(part_name='test_part', price='19.99')
            db.session.add(self.inventory)
            db.session.commit()

        self.client = self.app.test_client()
    
    def login(self):
        credentials = {
            'email': 'customer@test.com',
            'password': 'test'
        }

        response = self.client.post('/customers/login', json=credentials)
        return response.json['token']
    
    def test_create_service_ticket(self):
        service_ticket_payload = {
            'vin': 'vintest',
            'service_date': '1999-01-01',
            'service_desc': 'test_description',
            'customer_id': self.customer.id
        }

        response = self.client.post('/service_tickets/', json=service_ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['service_date'], '1999-01-01')
        self.assertEqual(response.json['vin'], 'vintest')
        self.assertEqual(response.json['service_desc'], 'test_description')
        self.assertEqual(response.json['customer_id'], self.customer.id)

    def test_invalid_service_ticket(self):
        service_ticket_payload = {
            'vin': 'vintest',
            'service_date': '1999-01-01',
            'customer_id': self.customer.id
        }

        response = self.client.post('/service_tickets/', json=service_ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['service_desc'], ['Missing data or required fields'])
    
    def get_all_service_tickets(self):
        response = self.client.get('/service_tickets')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['service_desc'], 'test_service')

    def test_get_all_tickets_for_a_customer(self):

        headers = {
            'Authorization': 'Bearer ' + self.login()
        }

        response = self.client.get('/customers/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['service_desc'], 'test_service')
    
    def test_add_mechanic_ticket(self):
        
        ticket_update_payload = {
            'add_mechanic_ids': [1],
            'remove_mechanic_ids': []
        }

        response = self.client.put('/service_tickets/1/edit', json=ticket_update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['mechanics']), 1)
        self.assertEqual(response.json['mechanics'][0]['id'], 1)

    def test_remove_mechanic_from_ticket(self):
        ticket_update_payload = {
            'add_mechanic_ids': [],
            'remove_mechanic_ids': [1]
        }

        response = self.client.put('/service_tickets/1/edit', json=ticket_update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['mechanics'], 0)

    def test_add_inventory_to_ticket(self):
        inventory_payload = {
            'inventory_id': self.inventory.id,
            'quantity': 3
        }

        response = self.client.post(f'/service_tickets/{self.service_ticket.id}/add-inventory', json=inventory_payload)
        self.assertEqual(response.status_code, 200)

        #Verfify db state for junction table
        with self.app.app_context():
            result = db.session.query(Service_ticketInventory).filter_by(service_ticket_id=self.service_ticket.id, inventory_id=self.inventory.id).first()
        
        self.assertIsNotNone(result)
        self.assertEqual(result.quantity, 3)