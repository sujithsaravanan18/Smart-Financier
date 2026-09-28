from flask import Blueprint

bp = Blueprint('loans', __name__)

from app.loans import routes
