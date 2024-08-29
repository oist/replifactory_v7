import flask
from flask import request
from flask_security.decorators import auth_required

from biofactory.devices.step_motor import MotorProfile
from biofactory.server import machine_manager
from biofactory.server.api import api
from biofactory.util.flask import NO_CONTENT, get_json_command_from_request


@api.route("/reactors", methods=["GET"])
@auth_required()
def get_reactors():
    return NO_CONTENT


@api.route("/reactors/<int:reactor_id>/command", methods=["POST"])
@auth_required()
def reactor_command(reactor_id):
    if not machine_manager.is_manual_control():
        return "Manual control is not enabled", 400
    machine = machine_manager.get_machine()
    if machine is None:
        return "Machine is not connected", 404
    try:
        reactor = machine.get_reactor(reactor_id)
    except IndexError:
        return f"There is no reactor with number {reactor_id}", 404
    valid_commands = reactor.get_command_info()
    command, data, _ = get_json_command_from_request(request, valid_commands)
    reactor.cmd(command, no_wait=True, **data)
    return NO_CONTENT


@api.route("/machine/command", methods=["POST"])
@auth_required()
def machine_command():
    if not machine_manager.is_manual_control():
        return "Manual control is not enabled", 400
    machine = machine_manager.get_machine()
    if machine is None:
        return "Machine is not connected", 404
    valid_commands = machine.get_commands_info()
    command, data, _ = get_json_command_from_request(request, valid_commands)
    machine.cmd(command, **data, no_wait=True)
    return NO_CONTENT


@api.route("/devices/<device_id>/command", methods=["POST"])
@auth_required()
def device_command(device_id):
    if not machine_manager.is_manual_control():
        return "Manual control is not enabled", 400
    machine = machine_manager.get_machine()
    if machine is None:
        return "Machine is not connected", 404
    valid_commands = machine.get_devices_commands_info().get(device_id, {})
    command, data, _ = get_json_command_from_request(request, valid_commands)
    machine.execute_device_command(device_id, command, **data, no_wait=True)
    return NO_CONTENT


@api.route("/machine/command_queue", methods=["POST"])
@auth_required()
def machineCommandQueue():
    valid_commands = {
        "clear": [],
    }
    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    if command == "clear":
        machine_manager.command_queue_clear()

    return NO_CONTENT


@api.route("/machine/valve", methods=["POST"])
@auth_required()
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
        machine_manager.valve_open(device_id, tags=tags)
    elif command == "close":
        machine_manager.valve_close(device_id, tags=tags)

    return NO_CONTENT


@api.route("/machine/laser", methods=["POST"])
@auth_required()
def machineLaserCommand():
    valid_commands = {
        "on": ["deviceId"],
        "off": ["deviceId"],
    }
    command, data, response = get_json_command_from_request(request, valid_commands)
    if response is not None:
        return response

    tags = {"source:api", "api:machine.laser"}

    device_id = data["deviceId"]
    if command == "on":
        machine_manager.laser_on(device_id, tags=tags)
    elif command == "off":
        machine_manager.laser_off(device_id, tags=tags)

    return NO_CONTENT


@api.route("/machine/stirrer", methods=["POST"])
@auth_required()
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
        machine_manager.stirrer_set_speed(device_id, speed, tags=tags)

    return NO_CONTENT


@api.route("/machine/thermometer", methods=["POST"])
@auth_required()
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
        machine_manager.thermometer_measure(device_id, tags=tags)

    return NO_CONTENT


@api.route("/machine/odsensor", methods=["POST"])
@auth_required()
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
        machine_manager.odsensor_measure(device_id, tags=tags)

    return NO_CONTENT


@api.route("/machine/pump", methods=["POST"])
@auth_required()
def machinePumpCommand():
    valid_commands = {
        "pump": ["deviceId", "volume"],
        "stop": ["deviceId"],
        "set-profile": ["deviceId", "profile"],
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
        machine_manager.pump_pump(device_id, volume, speed, tags=tags)
    elif command == "stop":
        machine_manager.pump_stop(device_id, tags=tags)
    elif command == "set-profile":
        cmd_data = data["profile"]
        profile = MotorProfile(
            acceleration=float(cmd_data["acceleration"]),
            deceleration=float(cmd_data["deceleration"]),
            max_speed_rps=float(cmd_data["max_speed_rps"]),
            min_speed_rps=float(cmd_data["min_speed_rps"]),
            full_step_speed=int(cmd_data["full_step_speed"]),
            kval_hold=int(cmd_data["kval_hold"]),
            kval_run=int(cmd_data["kval_run"]),
            kval_acc=int(cmd_data["kval_acc"]),
            kval_dec=int(cmd_data["kval_dec"]),
            intersect_speed=int(cmd_data["intersect_speed"]),
            start_slope=int(cmd_data["start_slope"]),
            acceleration_final_slope=int(cmd_data["acceleration_final_slope"]),
            deceleration_final_slope=int(cmd_data["deceleration_final_slope"]),
            thermal_compensation_factor=int(cmd_data["thermal_compensation_factor"]),
            overcurrent_threshold=int(cmd_data["overcurrent_threshold"]),
            stall_threshold=int(cmd_data["stall_threshold"]),
            step_mode=int(cmd_data["step_mode"]),
            alarm_enable=int(cmd_data["alarm_enable"]),
            clockwise=(
                cmd_data["clockwise"]
                if isinstance(cmd_data["clockwise"], bool)
                else cmd_data["clockwise"].lower() == "true"
            ),
        )
        machine_manager.pump_set_profile(device_id, profile, tags=tags)

    return NO_CONTENT


@api.route("/machine/vial", methods=["POST"])
@auth_required()
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
        machine_manager.vial_add_media(device_id, volume, speed, tags=tags)
    elif command == "add_drug":
        machine_manager.vial_add_drug(device_id, volume, speed, tags=tags)
    elif command == "waste":
        machine_manager.vial_waste(device_id, volume, speed, tags=tags)

    return NO_CONTENT
