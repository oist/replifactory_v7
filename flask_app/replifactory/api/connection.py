import logging
from flask import jsonify, request
from flask_security.decorators import auth_required

from flask_app import machine_manager, settings
from flask_app.replifactory.api import api
from flask_app.replifactory.util.flask import NO_CONTENT, get_json_command_from_request


logger = logging.getLogger(__name__)


@api.route("/connection", methods=["GET"])
# @auth_required()
# @Permissions.STATUS.require(403)
def connectionState():
    current = machine_manager.get_current_connection()
    options = _get_options()
    return jsonify({"current": current, "options": options})


@api.route("/connection", methods=["POST"])
@auth_required()
# @no_firstrun_access
# @Permissions.CONNECTION.require(403)
def connectionCommand():
    valid_commands = {"connect": ["device_id"], "disconnect": [], "fake_ack": []}

    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    if command == "connect":
        connection_options = _get_options()

        device_id = data.get("device_id", None)
        if device_id is None or device_id not in connection_options["devices"]:
            return "device_id is invalid", 400
        if "save" in data and data["save"]:
            settings().connection.device_address = device_id
        if "autoconnect" in data:
            settings().connection.autoconnect = data["autoconnect"]
        settings().save()
        try:
            machine_manager.connect(device_address=device_id)
        except Exception as e:
            logger.exception("Error while connecting to usb device")
            return str(e), 500
    elif command == "disconnect":
        machine_manager.disconnect()

    return NO_CONTENT


def _get_options():
    return machine_manager.__class__.get_connection_options()
