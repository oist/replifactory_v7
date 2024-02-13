import atexit
import functools
import logging
import os
from http.client import HTTPException

from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_static_digest import FlaskStaticDigest
from pydantic_yaml import parse_yaml_file_as, to_yaml_file

from flask_app.replifactory.config import Config, settings
from flask_app.replifactory.database import db
from flask_app.replifactory.events import Events, eventManager
from flask_app.replifactory.machine.model_6 import Machine
from flask_app.replifactory.socketio import MachineNamespace
from flask_app.replifactory.usb_manager import usbManager
from flask_app.routes.device_routes import device_routes
from flask_app.routes.experiment_routes import experiment_routes
from flask_app.routes.service_routes import service_routes

machine = None

flask_static_digest = FlaskStaticDigest()

base_dir = os.path.dirname(os.path.abspath(__file__))
pid_file_path = os.path.join(base_dir, "data/flask_app.pid")

logging.basicConfig(
    level=os.environ.get("LOGGING_LEVEL", logging.INFO),
)
logging.getLogger("pyftdi.eeprom").setLevel(logging.DEBUG)

log = logging.getLogger(__name__)


def create_app():
    global settings

    app = Flask(__name__, static_folder="static/build", static_url_path="/")
    config_file = os.environ.get("REPLIFACTORY_CONFIG", "config.yml")
    app.config["REPLIFACTORY_CONFIG"] = config_file
    try:
        settings(parse_yaml_file_as(Config, config_file))
    except FileNotFoundError as exc:
        log.warning("There is no configuration file: %s", config_file)
        settings(Config())

    def save_settings():
        to_yaml_file(config_file, settings(), exclude_none=True)

    settings().set_save_callback(save_settings)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "replifactory.db")
    database_uri = os.environ.get("DATABASE_URI", f"sqlite:///{db_path}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    db.init_app(app)

    global machine
    machine = Machine()
    usb_manager = usbManager()

    CORS(app)

    def _setup_blueprints():
        from flask_app.replifactory.api import api
        from flask_app.replifactory.util.flask import make_api_error

        api_endpoints = ["/api"]
        registrators = [
            functools.partial(app.register_blueprint, api, url_prefix="/api"),
            functools.partial(app.register_blueprint, device_routes),
            functools.partial(app.register_blueprint, experiment_routes),
            functools.partial(app.register_blueprint, service_routes),
        ]

        # register everything with the system
        for registrator in registrators:
            registrator()

        @app.errorhandler(HTTPException)
        def _handle_api_error(ex):
            if any(map(lambda x: request.path.startswith(x), api_endpoints)):
                return make_api_error(ex.description, ex.code)
            else:
                return ex

    def _run_before_server_started():
        with app.app_context():
            db.create_all()
            # connect_device()  # connect to device on startu
        # socketio_cors_allowed_origins = "*" if environment == "development" else None
        socket_io_async_mode = "threading" if os.environ.get("FLASK_RUN_FROM_CLI") == "true" else "gevent"
        socketio = SocketIO(app, cors_allowed_origins="*", async_mode=socket_io_async_mode, path="socket.io")
        socketio.on_namespace(MachineNamespace(app=app, machine=machine, namespace="/machine"))
        # socketio.run(app)
        usb_manager.start_monitoring()

        def on_shutdown():
            log.info("Shutting down...")
            # usb_manager.stop_monitoring()
            # turn off observers and other threads here
            eventManager().fire(Events.SHUTDOWN)

        atexit.register(on_shutdown)
        eventManager().fire(Events.STARTUP)

    setattr(app, "run_before_server_started", _run_before_server_started)

    @app.route("/static/<path:path>")
    def send_report(path):
        return send_from_directory("static", path)

    @app.route("/help", defaults={"path": ""})
    @app.route("/help/<path:path>")
    def send_help(path):
        if path:
            return send_from_directory("static/help", path)
        return app.send_static_file("index.html")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return app.send_static_file("index.html")

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "not-secret-key")
    _setup_blueprints()
    flask_static_digest.init_app(app)

    return app


if __name__ == "__main__":
    create_app().run()
