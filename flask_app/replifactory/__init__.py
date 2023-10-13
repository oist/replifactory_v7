import logging
import os

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_static_digest import FlaskStaticDigest

from replifactory.database import db
from replifactory.socketio import MachineNamespace
from routes.device_routes import device_routes
from routes.experiment_routes import experiment_routes
from routes.service_routes import service_routes

flask_static_digest = FlaskStaticDigest()

base_dir = os.path.dirname(os.path.abspath(__file__))
pid_file_path = os.path.join(base_dir, "data/flask_app.pid")

logging.basicConfig(
    level=os.environ.get("LOGGING_LEVEL", logging.INFO),
)


def create_app():
    app = Flask(__name__, static_folder="static/build", static_url_path="/")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "not-secret-key")
    app.register_blueprint(device_routes)
    app.register_blueprint(experiment_routes)
    app.register_blueprint(service_routes)
    flask_static_digest.init_app(app)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "replifactory.db")
    database_uri = os.environ.get("DATABASE_URI", f"sqlite:///{db_path}")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

    db.init_app(app)
    with app.app_context():
        db.create_all()
        # connect_device()  # connect to device on startup

    CORS(app)

    # environment = os.environ.get("ENVIRONMENT", "production")
    # socketio_cors_allowed_origins = "*" if environment == "development" else None
    socketio = SocketIO(app, cors_allowed_origins="*")
    socketio.on_namespace(MachineNamespace("/machine"))
    socketio.run(app)

    @app.route("/static/<path:path>")
    def send_report(path):
        return send_from_directory("static", path)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def catch_all(path):
        return app.send_static_file("index.html")

    return app
