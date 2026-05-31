from app.extensions import ma
from app.models import Service_ticket
from marshmallow import fields
import re 

class Service_ticketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Service_ticket 
        include_fk = True
        #load_instance = True

class EditService_ticketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = (
            'add_mechanic_ids',
            'remove_mechanic_ids'
        )

service_ticket_schema = Service_ticketSchema()
service_tickets_schema = Service_ticketSchema(many=True)
edit_service_tickets_schema = EditService_ticketSchema()
return_service_tickets_schema = Service_ticketSchema(exclude=['customer_id'])