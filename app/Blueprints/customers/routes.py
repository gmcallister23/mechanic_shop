from .schemas import customer_schema, customers_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, db
from . import customers_bp
from app.extensions import limiter, cache

##API Routes

#Create customers
@customers_bp.route('/', methods=['POST'])
@limiter.limit('5 per day') #limit requests to certain number per timeframe
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalar_one_or_none()
    
    if existing_customer:
            return jsonify({'error': 'Email already associated with an account'}), 400
    
    new_customer = Customer(**customer_data)
    
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

#Retreive all customers
@customers_bp.route("/", methods=['GET'])
@cache.cached(timeout=60)
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return jsonify(customers_schema.dump(customers))

#Retreive customer by ID
@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return jsonify(customer_schema.dump(customer)), 200
    return jsonify({"error": "Customer not found."}), 404

#Update Customer
@customers_bp.route("/<int:customer_id>", methods=['PUT'])
@limiter.limit('4 per month')
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404
    
    try: 
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()
    return jsonify(customer_schema.dump(customer)), 200


#Delete Customer
@customers_bp.route("/<int:customer_id>", methods=['DELETE'])
@limiter.limit('5 per day')
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer: 
        return jsonify({'error': 'Customer not found.'}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f'Customer id: {customer_id}, successfully deleted.'}), 200
