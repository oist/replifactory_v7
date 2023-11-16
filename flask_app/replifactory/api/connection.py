from flask import abort, jsonify, request

from flask_app import machine
from flask_app.replifactory.api import api
from flask_app.replifactory.util.flask import NO_CONTENT, get_json_command_from_request

from flask_app import settings


@api.route("/connection", methods=["GET"])
# @Permissions.STATUS.require(403)
def connectionState():
    device_id = machine.get_current_connection()
    current = {
        "device_id": device_id,
    }
    return jsonify({"current": current, "options": _get_options()})


@api.route("/connection", methods=["POST"])
# @no_firstrun_access
# @Permissions.CONNECTION.require(403)
def connectionCommand():
    valid_commands = {"connect": [], "disconnect": [], "fake_ack": []}

    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    if command == "connect":
        connection_options = _get_options()

        device_id = data.get("device_id", None)
        if device_id is None or device_id not in connection_options["devices"]:
            abort(jsonify(description="device_id is invalid"), 400)
        if "save" in data and data["save"]:
            settings().connection.device_address = device_id
        if "autoconnect" in data:
            settings().connection.autoconnect = data["autoconnect"]
        settings().save()
        machine.connect(device_address=device_id)
    elif command == "disconnect":
        machine.disconnect()

    return NO_CONTENT


def _get_options():
    return machine.__class__.get_connection_options()
