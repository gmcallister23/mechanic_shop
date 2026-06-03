from .schemas import service_ticket_schema, service_tickets_schema, edit_service_tickets_schema, return_service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Service_ticket, Mechanic, Inventory, Service_ticketInventory, db
from . import service_tickets_bp
from app.utils.util import token_required

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
    return jsonify(service_ticket_schema.dump(service_ticket), {'message': f'Mechanic {mechanic_id} assigned to ticket'}), 200
    #return jsonify ({'message': f'Mechanic {mechanic_id} assigned to ticket {service_ticket_id}'}), 200

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

@service_tickets_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_service_tickets(customer_id):
    query = select(Service_ticket).where(Service_ticket.customer_id == customer_id)

    service_tickets = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service_tickets), 200


@service_tickets_bp.route('/<int:service_ticket_id>', methods=['PUT'])
def edit_service_ticket(service_ticket_id):
    try:
        ticket_edits = edit_service_tickets_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Service_ticket).where(Service_ticket.id == service_ticket_id)
    service_tickets = db.session.execute(query).scalars().first()

    for mechanic_id in ticket_edits['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in service_tickets.mechanic:
            service_tickets.mechanic.append(mechanic)

    for mechanic_id in ticket_edits['remove_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic and mechanic not in service_tickets.mechanic:
            service_tickets.mechanic.remove(mechanic)

    db.session.commit()
    return return_service_tickets_schema.jsonify(service_tickets)

@service_tickets_bp.route('/<int:service_ticket_id>/add-inventory', methods=['PUT'])
def add_part_to_service_ticket(service_ticket_id):
    
    inventory_id = request.json('inventory_id')
    quantity = request.json('quantity')

    service_ticket = db.session.get(Service_ticket, service_ticket_id)
    part = db.session.get(Inventory, inventory_id)

    if not service_ticket:
        return jsonify({'error': 'Ticket not found'}), 400
    
    if not part:
        return jsonify({'error': 'Part not found'}), 400
    
    service_ticket_part = Service_ticketInventory(
        service_ticket_id = service_ticket.id,
        inventory_id = part.id,
        quantity = quantity
    )
    
    db.session.add(service_ticket_part)
    db.session.commit()

    return jsonify({'messages': 'Part added to ticket'}), 200

