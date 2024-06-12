from flask import jsonify, request
from flask_app.replifactory.api import api
from flask_app.replifactory.experiment import experimentRegistry


@api.route("/experiments", methods=["GET"])
def get_experiments():
    return jsonify(experimentRegistry.list())


@api.route("/experiments/<experiment_id>", methods=["GET"])
def get_experiment_status(experiment_id):
    experiment = experimentRegistry.get(experiment_id)
    if experiment is None:
        return jsonify({"error": "Experiment not found"}), 404
    return jsonify(experiment.status())


@api.route("/experiments/<experiment_id>/start", methods=["POST"])
@api.route("/experiments/<experiment_id>/pause", methods=["POST"])
@api.route("/experiments/<experiment_id>/resume", methods=["POST"])
@api.route("/experiments/<experiment_id>/stop", methods=["POST"])
def experiment_basic_commands(experiment_id):
    command = request.endpoint.split("/")[-1] if request.endpoint else None
    return experiment_command(experiment_id, command)


@api.route("/experiments/<experiment_id>/<command>", methods=["POST"])
def experiment_command(experiment_id, command):
    experiment = experimentRegistry.get(experiment_id)
    if experiment is None:
        return jsonify({"error": "Experiment not found"}), 404
    try:
        method = getattr(experiment, command)
        params = request.get_json()
        method(**params)
    except AttributeError:
        return jsonify({"error": f"No command named {command}"}), 404
    return jsonify(experiment.status())
