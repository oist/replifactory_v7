from dataclasses import dataclass

from biofactory.experiment import Experiment
from biofactory.plugins import PluginMetadata, BiofactoryPlugin


@dataclass
class ExperimentPluginMetadata(PluginMetadata):
    experiment_class: str


class ExperimentPlugin(BiofactoryPlugin):
    experiment_class = Experiment
    kind = "experiment"
    metadata_class = ExperimentPluginMetadata

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_experiment_class(self) -> type[Experiment]:
        return self.experiment_class

    def _collect_metadata(self):
        metadata = super()._collect_metadata()
        metadata.update(
            {
                "experiment_class": self.get_experiment_class().get_class_fullname(),
            }
        )
        return metadata
