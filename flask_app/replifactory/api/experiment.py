import logging
from flask import jsonify, request
from flask_app.replifactory.api import api
from flask_app.replifactory.experiment import experimentRegistry
from flask_app.replifactory.experiment_manager import experimentManager


logger = logging.getLogger(__name__)


@api.route("/experiments/classes", methods=["GET"])
def get_experiments_classes():
    return jsonify(experimentRegistry.list())


@api.route("/experiments/<experiment_id>", methods=["GET"])
def get_experiment_state(experiment_id):
    try:
        experiment_state = experimentManager().get_state(experiment_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(experiment_state)


@api.route("/experiments", methods=["GET"])
def get_running_experiments():
    return jsonify(experimentManager().get_states())


@api.route("/experiments/<experiment_id>/start", methods=["POST"])
@api.route("/experiments/<experiment_id>/pause", methods=["POST"])
@api.route("/experiments/<experiment_id>/resume", methods=["POST"])
@api.route("/experiments/<experiment_id>/stop", methods=["POST"])
def experiment_basic_commands(experiment_id):
    command = request.path.split("/")[-1] if request.endpoint else None
    return experiment_command(experiment_id, command)


@api.route("/experiments/<experiment_id>/<command>", methods=["POST"])
def experiment_command(experiment_id, command):
    experiment_manager = experimentManager()
    try:
        method = getattr(experiment_manager, f"{command}_experiment")
        params = request.get_json()
        experiment_status = method(experiment_id, **params)
    except Exception as e:
        logger.exception(f"Error while executing command {command} for experiment {experiment_id}")
        return jsonify({"error": str(e)}), 500
    return jsonify(experiment_status)
