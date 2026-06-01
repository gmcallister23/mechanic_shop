from flask import Blueprint

inventory_bp = Blueprint('intentory_bp', __name__)

from . import routes