import os

from gevent import monkey

monkey.patch_all()

# flake8: noqa: E402
from dotenv import load_dotenv

# https://docs.gunicorn.org/en/latest/settings.html#settings

load_dotenv()

wsgi_app = "replifactory.app"

# Server Socket
PORT = os.environ.get("PORT", 5000)
bind = f":{PORT}"

# Worker Processes
# default_workers = multiprocessing.cpu_count() * 2 + 1
workers = os.environ.get("WORKERS", 1)
worker_class = "gevent"
timeout = int(os.getenv("WORKERS_TIMEOUT", 30))

# Server Mechanics
preload_app = os.environ.get("PRELOAD_APP", "true").lower() == "true"
