#funciton that produces flask apps

from flask import Flask
#absolute path from app.extensions import ma
from .extensions import ma, limiter, cache #relative path, using because we are in a sister folder
from .models import db
from .Blueprints.customers import customers_bp
from .Blueprints.mechanics import mechanics_bp
from .Blueprints.service_tickets import service_tickets_bp
from .Blueprints.inventory import inventory_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs' #URL for exposing swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml' #Our API URL (can of course be a local source)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API NAME"
    }
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')

    #initialize extensions

    ma.init_app(app)
    db.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)

    # register blueprints
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service_tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app