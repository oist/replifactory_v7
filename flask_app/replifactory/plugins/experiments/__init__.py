

from flask_app.replifactory.plugins import ReplifactoryPlugins


class ExperimentPlugin(ReplifactoryPlugins):
    def __init__(self, experiment_class, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._experiment_class = experiment_class

    def get_experiment_class(self):
        return self._experiment_class
