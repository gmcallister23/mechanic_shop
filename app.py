from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List
from datetime import date
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from sqlalchemy import select
from flask import request, jsonify

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Vjzs3455@localhost/mechanic_shop'

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)
ma = Marshmallow()

db.init_app(app)
ma.init_app(app)

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)

    service_tickets: Mapped[List['Service_ticket']] = db.relationship(back_populates='customer')

service_mechanics = db.Table(
    'service_mechanics', 
    Base.metadata,
    db.Column('service_ticket_id', db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.ForeignKey('mechanic.id'))

)

class Service_ticket(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    vin: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    service_date: Mapped[date] = mapped_column(db.Date)
    service_desc: Mapped[str] = mapped_column(db.String(1000), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))

    customer: Mapped['Customer'] = db.relationship(back_populates='service_tickets')
    mechanics: Mapped[List['Mechanic']] = db.relationship(secondary=service_mechanics, back_populates = 'service_tickets')

class Mechanic(Base): 
    __tablename__ = 'mechanic'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)

    service_tickets: Mapped[List['Service_ticket']] = db.relationship(secondary=service_mechanics, back_populates='mechanics')

##Marshmallow Schemas

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer 
        #load_instance = True

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

##API Routes

#Create customers
@app.route('/customers', methods=['POST'])
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
@app.route("/customers", methods=['GET'])
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return jsonify(customers_schema.dump(customers))

#Retreive customer by ID
@app.route("/customers/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if customer:
        return jsonify(customer_schema.dump(customer)), 200
    return jsonify({"error": "Customer not found."}), 404

#Update Customer
@app.route("/customers/<int:customer_id>", methods=['PUT'])
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
@app.route("/customers/<int:customer_id>", methods=['DELETE'])
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer: 
        return jsonify({'error': 'Customer not found.'}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': f'Customer id: {customer_id}, successfully deleted.'}), 200

def reset_database():
    db.drop_all()
    db.create_all()

if __name__== "__main__":
    with app.app_context():
        #reset_database()
        db.create_all()

    app.run(debug=True)

