from flask import abort, jsonify, request

from replifactory import machine, settings
from replifactory.api import api
from replifactory.util.flask import NO_CONTENT, get_json_command_from_request


@api.route("/connection", methods=["GET"])
# @Permissions.STATUS.require(403)
def connectionState():
    state, bus, address = machine.get_current_connection()
    current = {
        "state": state,
        "bus": bus,
        "address": address,
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
        connection_options = machine.__class__.get_connection_options()

        device_address = data.get("device_address", None)
        if device_address is None or device_address not in connection_options["device_address"]:
            abort(jsonify(description="device_path is invalid"), 400)
        if "save" in data and data["save"]:
            settings().connection.device_address = device_address
        if "autoconnect" in data:
            settings().connection.autoconnect = data["autoconnect"]
        settings().save()
        machine.connect(device_address=device_address)
    elif command == "disconnect":
        machine.disconnect()

    return NO_CONTENT


def _get_options():
    connection_options = machine.__class__.get_connection_options()

    options = {
        "device_path": connection_options["device_path"],
    }

    return options
