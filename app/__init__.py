#funciton that produces flask apps

from flask import Flask
#absolute path from app.extensions import ma
from .extensions import ma, limiter #relative path, using because we are in a sister folder
from .models import db
from .Blueprints.customers import customers_bp
from .Blueprints.mechanics import mechanics_bp
from .Blueprints.service_tickets import service_tickets_bp

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    #initialize extensions

    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    
    # register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service_tickets')

    return app