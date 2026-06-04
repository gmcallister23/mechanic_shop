from .schemas import customer_schema, customers_schema, login_schema
from ..service_tickets.schemas import service_tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from app.models import Customer, Service_ticket, db
from . import customers_bp
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required

#Customer login

@customers_bp.route('/login', methods=['POST'])
def login():

    try:

        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    
    except ValidationError as e:
        return jsonify(e.messages), 400

    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()

    if customer and customer.password == password:
        token = encode_token(customer.id)

        response = {
            'status': 'success',
            'message': 'Suscessfully logged in.',
            'token': token
        }

        return jsonify(response), 200
    
    else:
        return jsonify({'message': 'invalid email or password'}),401

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
#@cache.cached(timeout=60)
def get_customers():
    try: 
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customer_schema.jsonify(customers), 200
    except:    
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

#Get all tickets for a specific customer
@customers_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    tickets = db.session.execute(select(Service_ticket).where(Service_ticket.customer_id == customer_id)).scalars().all()

    return jsonify(service_tickets_schema.dump(tickets)), 200


#Update Customer
@customers_bp.route("/<int:customer_id>", methods=['PUT'])
@limiter.limit('4 per month')
@token_required
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
@customers_bp.route("/<int:customer_id>", methods=['DELETE']) #removed customer_id paramater, because token_required holds user information
@limiter.limit('5 per day')
@token_required
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer: 
        return jsonify({'error': 'Customer not found.'}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f'Customer id: {customer_id}, successfully deleted.'}), 200
