import atexit
import functools
import inspect
import logging
import os
from http.client import HTTPException

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_security.core import Security
from flask_security.datastore import SQLAlchemyUserDatastore
from flask_security.models import fsqla_v3 as fsqla
from flask_security.utils import hash_password
from flask_socketio import SocketIO
from flask_static_digest import FlaskStaticDigest
from flask_wtf.csrf import CSRFProtect
from pydantic_yaml import parse_yaml_file_as, to_yaml_file
from whitenoise import WhiteNoise

from biofactory.config import Config, settings
from biofactory.database import db
from biofactory.events import Events, eventManager
from biofactory.experiment import register_experiment
from biofactory.experiment_manager import experimentManager
from biofactory.machine import biofactory_virtual, machineRegistry, replifactory_v5
from biofactory.machine_manager import machineManager
from biofactory.plugins import pluginsManager
from biofactory.plugins.experiments import ExperimentPlugin
from biofactory.server.socketio import MachineNamespace
from biofactory.usb_manager import usbManager

machine_manager = None

flask_static_digest = FlaskStaticDigest()

logging.basicConfig(
    level=os.environ.get("LOGGING_LEVEL", logging.INFO),
)
logging.getLogger("pyftdi.eeprom").setLevel(logging.INFO)
logging.getLogger("biofactory.drivers").setLevel(logging.INFO)
logging.getLogger("biofactory.events").setLevel(logging.INFO)
logging.getLogger("biofactory.devices").setLevel(logging.INFO)

log = logging.getLogger(__name__)


def create_app():
    # global settings

    # app = Flask(__name__, static_folder="static/build", static_url_path="/")
    app = Flask(__name__, static_folder="static")

    # Generate a nice key using secrets.token_urlsafe()
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "not-secret-key")
    # Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
    # Generate a good salt using: secrets.SystemRandom().getrandbits(128)
    app.config["SECURITY_PASSWORD_SALT"] = os.environ.get(
        "SECURITY_PASSWORD_SALT", "146585145368132386173505678016728509634"
    )
    # have session and remember cookie be samesite (flask/flask_login)
    app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
    app.config["SESSION_COOKIE_SAMESITE"] = "strict"

    config_file = os.environ.get("BIOFACTORY_CONFIG", "config.yml")
    app.config["BIOFACTORY_CONFIG"] = config_file
    try:
        settings(parse_yaml_file_as(Config, config_file))
    except FileNotFoundError:
        log.warning("There is no configuration file: %s", config_file)
        settings(Config())

    def save_settings():
        to_yaml_file(config_file, settings(), exclude_none=True)

    settings().set_save_callback(save_settings)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "biofactory.db")
    database_uri = os.environ.get("DATABASE_URI", f"sqlite:///{db_path}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    # As of Flask-SQLAlchemy 2.4.0 it is easy to pass in options directly to the
    # underlying engine. This option makes sure that DB connections from the
    # pool are still valid. Important for entire application since
    # many DBaaS options automatically close idle connections.
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Define models
    fsqla.FsModels.set_db_info(db)

    class Role(db.Model, fsqla.FsRoleMixin):
        pass

    class User(db.Model, fsqla.FsUserMixin):
        pass

    app.config.update(
        # no forms so no concept of flashing
        SECURITY_FLASH_MESSAGES=False,
        # Need to be able to route backend flask API calls. Use 'accounts'
        # to be the Flask-Security endpoints.
        SECURITY_URL_PREFIX="/security",
        # Turn on all the great Flask-Security features
        SECURITY_RECOVERABLE=True,
        SECURITY_TRACKABLE=True,
        SECURITY_CHANGEABLE=True,
        SECURITY_CONFIRMABLE=False,
        SECURITY_REGISTERABLE=True,
        # SECURITY_UNIFIED_SIGNIN=True,
        # These need to be defined to handle redirects
        # As defined in the API documentation - they will receive the relevant context
        SECURITY_LOGIN_URL="/login",
        SECURITY_LOGOUT_URL="/logout",
        SECURITY_POST_LOGOUT_VIEW="/",
        SECURITY_POST_CONFIRM_VIEW="/confirmed",
        SECURITY_CONFIRM_ERROR_VIEW="/confirm-error",
        SECURITY_RESET_VIEW="/reset-password",
        SECURITY_RESET_ERROR_VIEW="/reset-password-error",
        SECURITY_REDIRECT_BEHAVIOR="spa",
        # CSRF protection is critical for all session-based browser UIs
        # enforce CSRF protection for session / browser - but allow token-based
        # API calls to go through
        SECURITY_CSRF_PROTECT_MECHANISMS=["session", "basic"],
        SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS=True,
        # Send Cookie with csrf-token. This is the default for Axios and Angular.
        SECURITY_CSRF_COOKIE_NAME="XSRF-TOKEN",
        WTF_CSRF_CHECK_DEFAULT=False,
        WTF_CSRF_TIME_LIMIT=None,
        # For development
        SECURITY_REDIRECT_HOST=os.environ.get("REDIRECT_HOST", "localhost:8000"),
    )
    # In your app
    # Enable CSRF on all api endpoints.
    CSRFProtect(app)

    # app.config["SECURITY_REDIRECT_HOST"] = "localhost:8080"

    # Setup Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)

    global machine_manager, usb_manager, experiment_manager
    machine_manager = machineManager()
    experiment_manager = experimentManager()
    usb_manager = usbManager()

    CORS(app)

    def _setup_blueprints(flask_app):
        from biofactory.server.api import api
        from biofactory.util.flask import make_api_error

        api_endpoints = ["/api"]
        registrators = [
            functools.partial(app.register_blueprint, api, url_prefix="/api"),
        ]

        # register everything with the system
        for registrator in registrators:
            registrator()

        @app.errorhandler(HTTPException)
        def _handle_api_error(ex):
            if any(request.path.startswith(x) for x in api_endpoints):
                return make_api_error(ex.description, ex.code)
            else:
                return ex

    def _run_before_server_started():
        with app.app_context():
            db.create_all()
            if not app.security.datastore.find_user(email="fedor.gagarin@oist.jp"):
                app.security.datastore.create_user(
                    email="fedor.gagarin@oist.jp", password=hash_password("password")
                )
            db.session.commit()
            # connect_device()  # connect to device on startu
        # socketio_cors_allowed_origins = "*" if environment == "development" else None
        socket_io_async_mode = (
            "threading" if os.environ.get("FLASK_RUN_FROM_CLI") == "true" else "gevent"
        )
        socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode=socket_io_async_mode,
            path="socket.io",
        )
        socketio.on_namespace(MachineNamespace(app=app, namespace="/machine"))
        # socketio.run(app)
        usb_manager.start_monitoring()

        def on_shutdown():
            log.info("Shutting down...")
            # usb_manager.stop_monitoring()
            # turn off observers and other threads here
            eventManager().fire(Events.SHUTDOWN)

        atexit.register(on_shutdown)
        eventManager().fire(Events.STARTUP)

    app.run_before_server_started = _run_before_server_started

    # @app.route("/help", defaults={"path": ""})
    # @app.route("/help/<path:path>")
    # def send_help(path):
    #     if path:
    #         return send_from_directory("static/help/", path)
    #     return app.send_static_file("index.html")
    # @app.route("/help")
    # def send_help():
    #     return app.send_static_file("index.html")

    app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(script_dir, "static/"))
    app.wsgi_app.add_files(os.path.join(script_dir, "static/build/"))

    ui_endpoints = [
        "login",
        "home",
        "machine",
        "experiments",
        "maintance",
    ]

    @app.route("/")
    def ui_index_endpoint():
        return send_from_directory("static/build", "index.html")

    # only /help/ should return ui endpoint
    # /help/* should return ui static
    @app.route("/help/")
    def ui_help_endpoint():
        return send_from_directory("static/build", "index.html")

    @app.route("/<path:path>")
    def ui_static(path):
        for route in ui_endpoints:
            if path.startswith(route):
                return send_from_directory("static/build", "index.html")
        return send_from_directory("static/build", path)

    _setup_blueprints(app)
    flask_static_digest.init_app(app)

    machineRegistry().register(
        replifactory_v5.ReplifactoryMachine, replifactory_v5.check_compatible
    )
    machineRegistry().register(
        biofactory_virtual.VirtualBiofactoryMachine,
        biofactory_virtual.check_compatible,
    )
    pluginsManager().discover_plugins()

    for plugin in pluginsManager().get_plugins_instanceof(ExperimentPlugin):
        register_experiment(plugin.get_experiment_class())

    @app.route("/api/plugins")
    def get_plugins():
        plugins = []
        for plugin in pluginsManager().get_plugins():
            metadata = plugin.get_metadata()
            for ui_module in metadata.ui_modules:
                # Prepend the /plugins/<plugin_id> prefix to the ui_module_path
                plugin_id = plugin.get_metadata().id
                ui_module.path = f"/plugins/{plugin_id}/{ui_module.path}"
            plugins.append(metadata)
        return jsonify(plugins)

    @app.route("/plugins/<plugin_id>/<path:path>")
    def serve_plugin_static(plugin_id, path):
        plugin = pluginsManager().get_plugin(plugin_id)
        if plugin:
            # Get the file path of the plugin's module
            plugin_module_file = inspect.getfile(plugin.__class__)
            # Get the directory of the plugin's module
            plugin_dir = os.path.dirname(plugin_module_file)
            # Construct the path to the plugin's static directory
            static_dir = os.path.join(plugin_dir, "static")
            # Serve the file from the plugin's static directory
            if path.endswith(".js") or path.endswith(".cjs"):
                return send_from_directory(
                    static_dir, path, mimetype="application/javascript"
                )
            else:
                return send_from_directory(static_dir, path)
        else:
            return "Plugin not found", 404

    @app.route("/static/<path:path>")
    def send_report(path):
        return send_from_directory("static", path)

    return app


def main():
    app = create_app()
    app.run_before_server_started()
    app.run()


if __name__ == "__main__":
    main()
