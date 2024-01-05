import flask
from flask import request

from flask_app import machine
from flask_app.replifactory.api import api
from replifactory.util.flask import NO_CONTENT, get_json_command_from_request


@api.route("/machine/command_queue", methods=["POST"])
def machineCommandQueue():
    valid_commands = {
        "clear": [],
    }
    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    if command == "clear":
        machine.command_queue_clear()

    return NO_CONTENT


@api.route("/machine/valve", methods=["POST"])
def machineValveCommand():
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


@api.route("/machine/stirrer", methods=["POST"])
def machineStirrerCommand():
    valid_commands = {
        "setSpeed": ["deviceId", "speed"],
    }
    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    tags = {"source:api", "api:machine.stirrer"}

    device_id = data["deviceId"]
    if command == "setSpeed":
        speed = int(data["speed"]) / 100.0
        machine.stirrer_set_speed(device_id, speed, tags=tags)

    return NO_CONTENT


@api.route("/machine/thermometer", methods=["POST"])
def machineThermometerCommand():
    valid_commands = {
        "measure": ["deviceId"],
    }
    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    tags = {"source:api", "api:machine.thermometer"}

    device_id = data["deviceId"]
    if command == "measure":
        machine.thermometer_measure(device_id, tags=tags)

    return NO_CONTENT


@api.route("/machine/odsensor", methods=["POST"])
def machineODSensorCommand():
    valid_commands = {
        "measure": ["deviceId"],
    }
    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    tags = {"source:api", "api:machine.odsensor"}

    device_id = data["deviceId"]
    if command == "measure":
        machine.odsensor_measure(device_id, tags=tags)

    return NO_CONTENT


@api.route("/machine/pump", methods=["POST"])
def machinePumpCommand():
    valid_commands = {
        "pump": ["deviceId", "volume"],
        "stop": ["deviceId"],
    }
    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    tags = {"source:api", "api:machine.pump"}

    device_id = data["deviceId"]
    if command == "pump":
        volume = None
        if data["volume"]:
            try:
                volume = float(data["volume"])
            except ValueError:
                flask.abort(400, description=f"Wrong volume value: {data['volume']}")
        speed = None
        if "speed" in data and data["speed"]:
            try:
                speed = float(data["speed"])
            except ValueError:
                flask.abort(400, description=f"Wrong speed value: {data['speed']}")
        machine.pump_pump(device_id, volume, speed, tags=tags)
    elif command == "stop":
        machine.pump_stop(device_id, tags=tags)

    return NO_CONTENT


@api.route("/machine/vial", methods=["POST"])
def machineVialCommand():
    valid_commands = {
        "add_media": ["deviceId", "volume", "speed"],
        "add_drug": ["deviceId", "volume", "speed"],
        "waste": ["deviceId", "volume", "speed"],
    }
    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    tags = {"source:api", "api:machine.vial"}
    device_id = data["deviceId"]
    volume = float(data["volume"])
    speed = float(data["speed"])
    if command == "add_media":
        machine.vial_add_media(device_id, volume, speed, tags=tags)
    elif command == "add_drug":
        machine.vial_add_drug(device_id, volume, speed, tags=tags)
    elif command == "waste":
        machine.vial_waste(device_id, volume, speed, tags=tags)

    return NO_CONTENT
