from flask_security.decorators import auth_required

from biofactory.server.api import api
from biofactory.util.flask import SUCCESS


@api.route("/security/verify", methods=["GET"])
@auth_required()
def verify():
    return SUCCESS
