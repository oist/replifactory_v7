from flask import Blueprint


api = Blueprint("api", __name__)

from . import connection as api_connection  # noqa: F401,E402
