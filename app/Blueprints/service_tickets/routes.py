from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Service_ticket, Mechanic, db
from . import service_tickets_bp

##Service Tickets API

#Create Service Ticket
@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    #query = select(Service_ticket).where(Service_ticket.id == service_ticket_data['id'])
    #existing_service_ticket = db.session.execute(query).scalar_one_or_none()

    # if existing_service_ticket:
    #     return jsonify({'error': 'Id already associated with a service ticket'}), 400
    
    new_service_ticket = Service_ticket(**service_ticket_data)

    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201

#Update service ticket to add mechanic by id
@service_tickets_bp.route('/<int:service_ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(service_ticket_id, mechanic_id):
    
    service_ticket = db.session.get(Service_ticket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not service_ticket or not mechanic:
        return jsonify({'error': 'Ticket or Mechanic not found'}), 404
    
    if mechanic not in service_ticket.mechanics:
        service_ticket.mechanics.append(mechanic)

    db.session.commit()

    return jsonify ({'message': f'Mechanic {mechanic_id} assigned to ticket {service_ticket_id}'}), 200

#Update service ticket to remove the mechanic by id - removes the relationship between mechanic and service ticket
@service_tickets_bp.route('/<int:service_ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(service_ticket_id, mechanic_id):

    service_ticket = db.session.get(Service_ticket, service_ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not service_ticket or not mechanic:
        return {'error': 'Service ticket or Mechanic not found'}, 404
    
    if mechanic not in service_ticket.mechanics:
        return {'error': 'Mechanic not assigned to this ticket'}, 400
    
    service_ticket.mechanics.remove(mechanic)

    return {'message': f'Mechanc {mechanic_id} removed from ticket {service_ticket_id}'}

#Retreive all tickets
@service_tickets_bp.route('/', methods=['GET'])
def get_service_tickets():
    query = select(Service_ticket)
    service_tickets = db.session.execute(query).scalars().all()

    return jsonify(service_ticket_schema.dump(service_tickets))



