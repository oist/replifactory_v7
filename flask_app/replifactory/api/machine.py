from flask import request

from flask_app import machine
from flask_app.replifactory.api import api
from replifactory.util.flask import NO_CONTENT, get_json_command_from_request


@api.route("/machine/valve", methods=["POST"])
def printerToolCommand():
    valid_commands = {
        "open": ["deviceId"],
        "close": ["deviceId"],
        # "test": ["deviceId"],
    }
    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    tags = {"source:api", "api:machine.valve"}

    device_id = data["deviceId"]
    if command == "open":
        machine.valve_open(device_id, tags=tags)
    elif command == "close":
        machine.valve_close(device_id, tags=tags)

    return NO_CONTENT
