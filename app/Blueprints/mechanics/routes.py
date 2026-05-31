from .schemas import mechanic_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Mechanic, db
from . import mechanics_bp

#Mechanic Routes

#Create mechanic

@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == mechanic_data['email'])
    existing_mechanic = db.session.execute(query).scalar_one_or_none()

    if existing_mechanic:
        return jsonify({'error': 'Email is already associated with account'}), 400
    
    new_mechanic = Mechanic(**mechanic_data)

    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

#Retreive All Mechanics
@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():

    try: 
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page)
        return mechanics_schema.jsonify(mechanics), 200
    except:    

        query = select(Mechanic)
        mechanics = db.session.execute(query).scalars().all()

        return jsonify(mechanics_schema.dump(mechanics))

#pagination: /books?page=(int)&per_page=(int)

#Retreive mechanic by ID
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
def get_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if mechanic:
        return jsonify(mechanic_schema.dump(mechanic)), 200
    return jsonify({'error': 'Customer not found.'}), 404

#Update Mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({'error': 'Mechanic not found'}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return jsonify(mechanic_schema.dump(mechanic)), 200

#Delete Mechanic
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not mechanic:
        return jsonify({'error': 'Mechanic not found.'}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({'message': f'Mechanic id: {mechanic_id}, successfully deleted'}), 200

#popular mechanics
@mechanics_bp.route('/popular', methods=['GET'])
def popular_mechanics():

    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key= lambda mechanic: len(mechanic.service_tickets), reverse=True)#param : #expression ) 
    
    return mechanic_schema.jsonify(mechanics)

    # for mechanic in mechanics: 
    #     print(mechanic.name, len(mechanic.service_tickets) )

@mechanics_bp.route('/search', methods=['GET'])
def search_mechanics():
    name = request.args.get('name')

    query = select(Mechanic).where(Mechanic.name.like(name))
    #query = select(Mechanic).where(Mechanic.name.like(f'%{name}%')) this adds wildcards, so that anything that matches the search shows up
    mechanics = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics)

