# plugin/manager.py
import os
import sys
import json
import importlib.util
import inspect
from typing import Dict, List, Optional, Any
from .base import PluginBase, SearchResult
from console import DHConsole

class PluginManager:
    """Manages plugin loading, configuration, and execution"""
    
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.console = DHConsole()
            cls._instance.plugins = {}
            cls._instance.config = {}
            cls._instance._initialize()
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'plugins'):
            self.plugins: Dict[str, PluginBase] = {}
        if not hasattr(self, 'config'):
            self.config: Dict[str, Dict[str, Any]] = {}
        if not hasattr(self, 'console'):
            self.console = DHConsole()
    
    def _initialize(self):
        """Initialize the plugin manager"""
        self.load_config()
        self.load_all_plugins()
    
    def load_config(self):
        """Load plugin configuration from JSON file"""

        config_path = None
        if getattr(sys, 'frozen', False):
            config_path = os.path.join(os.path.dirname(sys.executable), "./plugins/config.json")
        else:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")

        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
            self.save_config()

    def save_config(self):
        """Save current configuration to JSON file"""
        config_path = None
        if getattr(sys, 'frozen', False):
            config_path = os.path.join(os.path.dirname(sys.executable), "./plugins/config.json")
        else:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def load_all_plugins(self):
        """Load both builtin and custom plugins"""
        self.load_builtin_plugins()
        self.load_custom_plugins()
    
    def load_builtin_plugins(self):
        """Load plugins from the builtin directory"""
        builtin_dir = None
        if getattr(sys, 'frozen', False):
            builtin_dir = os.path.join(os.path.dirname(sys.executable), "./plugins/builtin")
            if not os.path.exists(builtin_dir):
                os.makedirs(builtin_dir)
        else:
            builtin_dir = os.path.join(os.path.dirname(__file__), "builtin")

        self.console.print(f"Loading builtin plugins from d[<f=FFFFFF>, <{builtin_dir}>]")
        self._load_plugins_from_directory(builtin_dir)
    
    def load_custom_plugins(self):
        """Load plugins from the custom directory"""
        custom_dir = None
        if getattr(sys, 'frozen', False):
            custom_dir = os.path.join(os.path.dirname(sys.executable), "./plugins/custom")
            if not os.path.exists(custom_dir):
                os.makedirs(custom_dir)
        else:
            custom_dir = os.path.join(os.path.dirname(__file__), "custom")

        self.console.print(f"Loading custom plugins from d[<f=FFFFFF>, <{custom_dir}>]")
        self._load_plugins_from_directory(custom_dir)
    
    def _load_plugins_from_directory(self, directory: str):
        """Load plugin modules from a directory"""
        if not os.path.exists(directory):
            return

        for filename in os.listdir(directory):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    path = os.path.join(directory, filename)
                    spec = importlib.util.spec_from_file_location(filename[:-3], path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Find and register plugin classes
                        for _, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and 
                                issubclass(obj, PluginBase) and 
                                obj != PluginBase):
                                plugin = obj()
                                self.register_plugin(plugin)
                                
                except Exception as e:
                    print(f"Error loading plugin {filename}: {e}")
    
    def register_plugin(self, plugin: PluginBase):
        """Register a new plugin"""
        self.plugins[plugin.name] = plugin
        # Initialize config for new plugin if needed
        if plugin.name not in self.config:
            self.config[plugin.name] = {
                "enabled": True,
                "config": {k: v.get("default") 
                          for k, v in plugin.get_config_fields().items()}
            }
            self.save_config()
    
    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Get a plugin by name"""
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, PluginBase]:
        """Get all registered plugins"""
        return self.plugins.copy()
    
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]):
        """Set configuration for a plugin"""
        if plugin_name not in self.config:
            self.config[plugin_name] = {}
        self.config[plugin_name]["config"] = config
        self.save_config()
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get configuration for a plugin"""
        return self.config.get(plugin_name, {}).get("config", {})
    
    def set_api_key(self, plugin_name: str, api_key: str):
        """Set API key for a plugin"""
        if plugin_name not in self.config:
            self.config[plugin_name] = {}
        self.config[plugin_name]["api_key"] = api_key
        self.save_config()
    
    def get_api_key(self, plugin_name: str) -> Optional[str]:
        """Get API key for a plugin"""
        return self.config.get(plugin_name, {}).get("api_key")
    
    def enable_plugin(self, plugin_name: str):
        """Enable a plugin"""
        if plugin_name in self.config:
            self.config[plugin_name]["enabled"] = True
            self.save_config()
    
    def disable_plugin(self, plugin_name: str):
        """Disable a plugin"""
        if plugin_name in self.config:
            self.config[plugin_name]["enabled"] = False
            self.save_config()
    
    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """Check if a plugin is enabled"""
        return self.config.get(plugin_name, {}).get("enabled", True)
    
    async def search_all(self, query: str) -> Dict[str, List[SearchResult]]:
        """
        Execute search across all enabled plugins
        
        Args:
            query: Search query string
            
        Returns:
            Dict mapping plugin names to their search results
        """
        results = {}
        for name, plugin in self.plugins.items():
            if self.is_plugin_enabled(name):
                try:
                    config = self.get_plugin_config(name)
                    results[name] = await plugin.search(query, config)
                except Exception as e:
                    print(f"Error executing plugin {name}: {e}")
                    results[name] = []
        return results