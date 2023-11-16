from flask_app import create_app


application = create_app()
application.run_before_server_started()
