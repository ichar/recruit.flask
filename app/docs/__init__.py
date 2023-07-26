from flask import Blueprint

docs_bp = Blueprint('docs_bp', __name__, template_folder='templates', static_folder='static')

from . import views, errors
