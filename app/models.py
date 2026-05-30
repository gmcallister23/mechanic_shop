#from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List
from datetime import date

#from marshmallow import ValidationError
#from sqlalchemy import select
#from flask import request, jsonify

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class = Base)


#db.init_app(app) only using init in the init file


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
    vin: Mapped[str] = mapped_column(db.String(255), nullable=False)
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
