from flask import Blueprint


api = Blueprint("api", __name__)

from . import connection as api_connection  # noqa: F401,E402
from . import machine as api_machine  # noqa: F401,E402
from . import security as api_security  # noqa: F401,E402
