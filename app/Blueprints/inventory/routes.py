from .schemas import inventory_schema, inventory_schemas
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Inventory, db
from . import inventory_bp
from sqlalchemy import select

#Post
@inventory_bp.route('/', methods=['POST'])
def create_inventory():
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Inventory).where(Inventory.part_name == inventory_data['part_name'])
    existing_part = db.session.execute(query).scalar_one_or_none()

    if existing_part:
        return jsonify({'error': 'Part name is already associated with a part in the inventory'}), 400
    
    new_part = Inventory(**inventory_data)

    db.session.add(new_part)
    db.session.commit()
    return inventory_schema.jsonify(new_part), 201

#Get
@inventory_bp.route('/', methods=['GET'])
def get_all_inventory():
        query = select(Inventory)
        inventory = db.session.execute(query).scalars().all()

        return jsonify(inventory_schema.dump(inventory))


@inventory_bp.route('/<int: invenotory_id>', methods=['GET'])
def get_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if inventory:
         return jsonify(inventory_schema.dump(inventory)), 200
    return jsonify({'error': 'Inventory not found'}), 404

#Put
@inventory_bp.route('/<int: inventory_id>', methods=['PUT'])
def update_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({'error': 'Inventory part not found.'}), 404
    
    try:
        inventory_data = inventory_schema.load(request.json)

    except ValidationError as e:
         return jsonify(e.messages), 400
    
    for key, value in inventory_data.items():
         setattr(inventory, key, value)
        
    db.session.commit()
    return jsonify(inventory_schema.dump(inventory)), 200

#Delete
@inventory_bp.route('/<int: inventory_id>', methods=['DELETE'])
def delete_inventory(inventory_id):
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({'error': 'Inventory part not found'}), 404
    
    db.session.delete(inventory)
    db.session.commit()
    return jsonify({'message': f'Inventory id: {inventory_id}, successfully deleted'}), 200
    
    