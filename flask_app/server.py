import logging
import multiprocessing
import os
import signal

from gunicorn.app.wsgiapp import WSGIApplication

from flask_app import create_app

base_dir = os.path.dirname(os.path.abspath(__file__))
pid_file_path = os.path.join(base_dir, "data/flask_app.pid")

logging.basicConfig(
    level=os.environ.get("LOGGING_LEVEL", logging.INFO),
)


class StandaloneApplication(WSGIApplication):
    def __init__(self, app_uri, options=None):
        self.options = options or {}
        self.app_uri = app_uri
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)


def run():
    options = {
        "bind": "0.0.0.0:5000",
        "workers": (multiprocessing.cpu_count() * 2) + 1,
        "worker_class": "eventlet",
    }
    StandaloneApplication("flask_app.server:app", options).run()


script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, '../db/replifactory.db')
os.environ.setdefault("DATABASE_URI", f'sqlite:///{db_path}')

app = create_app()

pid = os.getpid()
with open(pid_file_path, "w+") as pid_file:
    pid_file.write(str(pid))


@app.route('/shutdown')
def shutdown():
    print("Shutting down server...")
    with open(pid_file_path, "r") as pid_file:
        pid = int(pid_file.read())
    try:
        app.device.disconnect_all()
    except:
        pass
    os.kill(pid, signal.SIGTERM)
    return {}, 200


if __name__ == "__main__":
    run()
