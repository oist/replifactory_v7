from dataclasses import dataclass
import logging
import os
import importlib


logger = logging.getLogger(__name__)


def discover_plugins(app, plugins_folder=None):
    plugins_folder = plugins_folder or os.path.dirname(__file__)
    if app is None:
        logger.warning("No app provided")
        return

    app.extensions.setdefault("replifactory_plugins", {})
    app_plugins = app.extensions["replifactory_plugins"]

    for plugin_category in os.listdir(plugins_folder):
        if plugin_category.startswith("_"):
            continue
        plugins_category_path = os.path.join(plugins_folder, plugin_category)
        if not os.path.isdir(plugins_category_path):
            continue
        for plugin_name in os.listdir(plugins_category_path):
            if plugin_name.startswith("_"):
                continue
            plugin_path = os.path.join(plugins_category_path, plugin_name)
            if not os.path.isdir(plugin_path):
                continue
            module_name = f"flask_app.replifactory.plugins.{plugin_category}.{plugin_name}.plugin"
            module = importlib.import_module(module_name)
            if hasattr(module, 'init_plugin'):
                plugin = module.init_plugin(app)
                if plugin.id in app_plugins:
                    raise ValueError(f"Plugin {plugin.name} with id {plugin.id} already exists")
                app_plugins[plugin.id] = plugin


@dataclass
class PluginUiModuleMetadata:
    moduleName: str
    path: str
    kind: str = "General"


@dataclass
class PluginMetadata:
    id: str
    name: str
    description: str
    kind: str
    ui_modules: list[PluginUiModuleMetadata]


class ReplifactoryPlugin:
    kind = "General"
    name = None

    def __init__(self, *args, **kwargs):
        self.id = f"{self.__module__}.{self.__class__.__name__}"
        self.name = self.name or self.id
        self.description = self.__doc__ or ""

    def get_ui_modules(self) -> list[PluginUiModuleMetadata]:
        """ Return a list of frontend modules to be loaded by the client
        e.g. [{"name": "myPlugin", "url": "/static/plugins/myPlugin.js"}]
        """
        return []

    def get_metadata(self):
        return PluginMetadata(
            id=self.id,
            name=self.name or self.id,
            description=self.description,
            kind=self.kind,
            ui_modules=self.get_ui_modules()
        )
