from flask_security.decorators import auth_required

from flask_app.replifactory.api import api
from flask_app.replifactory.util.flask import SUCCESS


@api.route("/security/verify", methods=["GET"])
@auth_required()
def verify():
    return SUCCESS
