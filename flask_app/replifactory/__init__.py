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

from replifactory.config import Config, settings
from replifactory.database import db
from replifactory.events import Events, eventManager
from replifactory.machine.model_6 import Machine
from replifactory.socketio import MachineEventListener, MachineNamespace
from routes.device_routes import device_routes
from routes.experiment_routes import experiment_routes
from routes.service_routes import service_routes

machine = None

flask_static_digest = FlaskStaticDigest()

base_dir = os.path.dirname(os.path.abspath(__file__))
pid_file_path = os.path.join(base_dir, "data/flask_app.pid")

logging.basicConfig(
    level=os.environ.get("LOGGING_LEVEL", logging.INFO),
)

log = logging.getLogger(__name__)


def create_app():
    global settings

    app = Flask(__name__, static_folder="static/build", static_url_path="/")
    config_file = os.environ.get("REPLIFACTORY_CONFIG", "config.yml")
    app.config["REPLIFACTORY_CONFIG"] = config_file
    try:
        settings(parse_yaml_file_as(Config, config_file))
    except FileNotFoundError as exc:
        log.warning("There is no configuration file: %s", config_file, exc_info=exc)
        settings(Config())

    def save_settings():
        to_yaml_file(config_file, settings(), exclude_none=True)

    settings().set_save_callback(save_settings)

    def _setup_blueprints():
        from replifactory.api import api
        from replifactory.util.flask import make_api_error

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

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "replifactory.db")
    database_uri = os.environ.get("DATABASE_URI", f"sqlite:///{db_path}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    db.init_app(app)
    with app.app_context():
        db.create_all()
        # connect_device()  # connect to device on startup

    CORS(app)

    global machine
    machine = Machine()

    # import should be after initialize global machine variable
    from replifactory.usbmonitor import UsbMonitor
    usb_monitor = UsbMonitor(app)

    # environment = os.environ.get("ENVIRONMENT", "production")
    # socketio_cors_allowed_origins = "*" if environment == "development" else None
    socketio = SocketIO(app, cors_allowed_origins="*")
    socketio.on_namespace(MachineNamespace(machine=machine, namespace="/machine"))
    socketio.run(app)

    MachineEventListener(app)

    @app.route("/static/<path:path>")
    def send_report(path):
        return send_from_directory("static", path)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return app.send_static_file("index.html")

    usb_monitor.start_monitoring()

    def on_shutdown():
        log.info("Shutting down...")
        usb_monitor.stop_monitoring()
        # turn off observers and other threads here
        # eventManager.fire(events.Events.SHUTDOWN)

    atexit.register(on_shutdown)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "not-secret-key")
    _setup_blueprints()
    flask_static_digest.init_app(app)

    eventManager().fire(Events.STARTUP)

    return app
