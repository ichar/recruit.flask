from flask import Blueprint
from app.auth.models import users

login_bp = Blueprint('login_bp', __name__, template_folder='templates', static_folder='static')
