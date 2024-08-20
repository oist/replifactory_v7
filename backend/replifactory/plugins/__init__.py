from dataclasses import dataclass
import logging
import os
import importlib


logger = logging.getLogger(__name__)

_instance = None


def pluginsManager():
    global _instance
    if _instance is None:
        _instance = PluginsManager()
    return _instance


class PluginsManager:

    def __init__(self):
        self._plugins = {}

    def discover_plugins(self, plugins_folder=None):
        plugins_folder = plugins_folder or os.path.dirname(__file__)
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
                module_name = (
                    f"replifactory.plugins.{plugin_category}.{plugin_name}.plugin"
                )
                module = importlib.import_module(module_name)
                if hasattr(module, "init_plugin"):
                    plugin = module.init_plugin()
                    self.add_plugin(plugin)

    def add_plugin(self, plugin):
        if plugin.id in self._plugins:
            raise ValueError(f"Plugin {plugin.name} with id {plugin.id} already exists")
        self._plugins[plugin.id] = plugin

    def get_plugin(self, plugin_id):
        return self._plugins.get(plugin_id)

    def get_plugins(self):
        return self._plugins.values()

    def get_plugins_with_kind(self, kind):
        return [plugin for plugin in self._plugins.values() if plugin.kind == kind]

    def get_plugins_instanceof(self, plugin_class):
        return [
            plugin
            for plugin in self._plugins.values()
            if isinstance(plugin, plugin_class)
        ]


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
    metadata_class = PluginMetadata

    def __init__(self, *args, **kwargs):
        self.id = f"{self.__module__}.{self.__class__.__name__}"
        self.name = self.name or self.id
        self.description = self.__doc__ or ""

    def get_ui_modules(self) -> list[PluginUiModuleMetadata]:
        """Return a list of frontend modules to be loaded by the client
        e.g. [{"name": "myPlugin", "url": "/static/plugins/myPlugin.js"}]
        """
        return []

    def get_metadata(self):
        return self.metadata_class(**self._collect_metadata())

    def _collect_metadata(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "kind": self.kind,
            "ui_modules": self.get_ui_modules(),
        }
