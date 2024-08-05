from flask_security.decorators import auth_required

from replifactory.server.api import api
from replifactory.util.flask import SUCCESS


@api.route("/security/verify", methods=["GET"])
@auth_required()
def verify():
    return SUCCESS
