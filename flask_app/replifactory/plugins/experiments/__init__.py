

from flask_app.replifactory.plugins import ReplifactoryPlugin


class ExperimentPlugin(ReplifactoryPlugin):
    experiment_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_experiment_class(self):
        return self.experiment_class

    def get_frontend_modules(self):
        return super().get_frontend_modules() + [
            # {"name": "desciption", "url": f"/static/{self.name}/description.js"},
            # {"name": "parameters", "url": f"/static/{self.name}/parameters.js"},
            # {"name": "parameters", "url": f"/static/{self.name}/replifactory_endless_growth_plugin.umd.cjs"},
        ]
