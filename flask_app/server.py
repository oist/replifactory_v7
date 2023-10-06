#server.py

import sys
import logging
import os
import signal

from flask import Flask, current_app, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_static_digest import FlaskStaticDigest
from waitress import serve

from experiment.models import db
from routes.device_routes import connect_device, device_routes
from routes.experiment_routes import experiment_routes
from routes.service_routes import service_routes

flask_static_digest = FlaskStaticDigest()

base_dir = os.path.dirname(os.path.abspath(__file__))
pid_file_path = os.path.join(base_dir, "data/flask_app.pid")

logging.basicConfig(
    level=os.environ.get("LOGGING_LEVEL", logging.INFO),
)

def create_app():
    pid = os.getpid()
    with open(pid_file_path, "w+") as pid_file:
        pid_file.write(str(pid))

    app = Flask(__name__, static_folder='static/build', static_url_path="/")
    app.register_blueprint(device_routes)
    app.register_blueprint(experiment_routes)
    app.register_blueprint(service_routes)
    flask_static_digest.init_app(app)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, '../db/replifactory.db')
    database_uri = os.environ.get("DATABASE_URI", f'sqlite:///{db_path}')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

    db.init_app(app)
    with app.app_context():
        db.create_all()
        # connect_device()  # connect to device on startup
    CORS(app)

    @app.route('/shutdown')
    def shutdown():
        print("Shutting down server...")
        with open(pid_file_path, "r") as pid_file:
            pid = int(pid_file.read())
        try:
            current_app.device.disconnect_all()
        except:
            pass
        os.kill(pid, signal.SIGTERM)

    @app.route('/static/<path:path>')
    def send_report(path):
        return send_from_directory('static', path)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return app.send_static_file("index.html")

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        logging.info("Starting server...")
        if "serve" in sys.argv:
            serve(app, host="0.0.0.0", port=5000, threads=1)
        else:
            app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
