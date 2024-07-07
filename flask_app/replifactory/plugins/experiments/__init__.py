

from flask_app.replifactory.plugins import ReplifactoryPlugin


class ExperimentPlugin(ReplifactoryPlugin):
    experiment_class = None
    kind = "experiment"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_experiment_class(self):
        return self.experiment_class
