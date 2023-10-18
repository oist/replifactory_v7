import logging
import os
import signal
import sys

from flask import current_app
from waitress import serve

import replifactory

base_dir = os.path.dirname(os.path.abspath(__file__))
pid_file_path = os.path.join(base_dir, "data/flask_app.pid")

logging.basicConfig(
    level=os.environ.get("LOGGING_LEVEL", logging.INFO),
)

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, '../db/replifactory.db')
    os.environ.setdefault("DATABASE_URI", f'sqlite:///{db_path}')

    app = replifactory.create_app()

    pid = os.getpid()
    with open(pid_file_path, "w+") as pid_file:
        pid_file.write(str(pid))

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
        return {}, 200

    with app.app_context():
        logging.info("Starting server...")
        if "serve" in sys.argv:
            serve(app, host="0.0.0.0", port=5000, threads=1)
        else:
            app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
