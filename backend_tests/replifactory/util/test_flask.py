from flask import Flask

from biofactory.util.flask import get_json_command_from_request


def test_get_json_command_from_request():
    valid_commands = {"connect": ["address"], "disconnect": [], "fake_ack": []}
    app = Flask(__name__)
    request_data = {"command": "connect", "address": "127.0.0.1"}
    with app.test_request_context("/endpoint", json=request_data) as context:
        command, data, response = get_json_command_from_request(
            context.request, valid_commands
        )
        assert command == "connect"
        assert data == {"address": "127.0.0.1"}
        assert response is None


def test_get_json_command_from_request_invalid_command():
    valid_commands = {"connect": ["address"], "disconnect": [], "fake_ack": []}
    app = Flask(__name__)
    request_data = {"command": "invalid"}
    with app.test_request_context("/endpoint", json=request_data) as context:
        try:
            get_json_command_from_request(context.request, valid_commands)
        except Exception as exc:
            assert str(exc) == "400 Bad Request: command is invalid"
        else:
            raise AssertionError("Expected an exception to be raised")


def test_get_json_command_from_request_extra_field():
    valid_commands = {"connect": ["address"], "disconnect": [], "fake_ack": []}
    app = Flask(__name__)
    request_data = {"command": "disconnect", "extra": "field"}
    with app.test_request_context("/endpoint", json=request_data) as context:
        try:
            get_json_command_from_request(context.request, valid_commands)
        except Exception as exc:
            assert str(exc) == "400 Bad Request: Extra parameters found: ['extra']"
        else:
            raise AssertionError("Expected an exception to be raised")
