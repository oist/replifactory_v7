from gevent import monkey

monkey.patch_all()

import sys

from gunicorn.app.wsgiapp import WSGIApplication

from replifactory.server import create_app

application = create_app()
application.run_before_server_started()


def run_gunicorn():
    # Add the configuration file to the arguments
    # sys.argv = ["gunicorn", "-c", "gunicorn.conf.py"]

    # Create and run the Gunicorn application
    WSGIApplication().run()


def main(*args, **kwargs):
    run_gunicorn()


if __name__ == "__main__":
    main()
