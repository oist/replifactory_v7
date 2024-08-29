import copy
import logging

import flask

log = logging.getLogger(__name__)


SUCCESS = {}
NO_CONTENT = ("", 204, {"Content-Type": "text/plain"})
NOT_MODIFIED = ("Not Modified", 304, {"Content-Type": "text/plain"})


def get_json_command_from_request(request, valid_commands):
    data = request.get_json()

    if "command" not in data or data["command"] not in valid_commands:
        log.warning(f"Invalid command: {data}")
        flask.abort(400, description="command is invalid")

    data_copy = copy.deepcopy(data)
    command = data_copy.pop("command")

    extra_params = [
        param for param in data_copy if param not in valid_commands[command]
    ]
    if extra_params:
        log.warning(f"Extra parameters found: {extra_params}")
        flask.abort(400, description=f"Extra parameters found: {extra_params}")

    return command, data_copy, None


def make_api_error(message, status):
    """
    Helper to generate API error responses in JSON format.

    Turns something like ``make_api_error("Not Found", 404)`` into a JSON response
    with body ``{"error": "Not Found"}``.

    Args:
        message: The error message to put into the response
        status: The HTTP status code

    Returns: a flask response to return to the client
    """
    return flask.make_response(flask.jsonify(error=message), status)
