import logging
import os
import importlib

from flask_app.replifactory.experiment import register_experiment


logger = logging.getLogger(__name__)


def discover_plugins(app, plugins_folder=None):
    plugins_folder = plugins_folder or os.path.dirname(__file__)
    if app is None:
        logger.warning("No app provided")
        return

    app.extensions.setdefault("replifactory_plugins", {
        "experiments": {},
    })
    app_experiments_plugins = app.extensions["replifactory_plugins"]["experiments"]

    experiments_plugins_folder = os.path.join(plugins_folder, 'experiments')
    for plugins_folder_item in os.listdir(experiments_plugins_folder):
        if plugins_folder_item.startswith("_"):
            continue
        plugin_full_path = os.path.join(experiments_plugins_folder, plugins_folder_item)
        if os.path.isdir(plugin_full_path):
            plugin_name = plugins_folder_item
            module_name = f"flask_app.replifactory.plugins.experiments.{plugin_name}.experiment"
            module = importlib.import_module(module_name)
            if hasattr(module, 'init_plugin'):
                experiment_plugin = module.init_plugin(app)
                app_experiments_plugins[plugin_name] = experiment_plugin


class ReplifactoryPlugins:
    pass
