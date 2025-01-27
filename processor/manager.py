#processor/manager.py
import os
import importlib.util
import inspect
from typing import Dict
from .base import ProcessorBase

class ProcessorManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.processors = {}
            cls._instance.load_all_processors()
        return cls._instance

    def load_all_processors(self):
        """Load both builtin and custom processors"""
        self.load_builtin_processors()
        self.load_custom_processors()

    def load_builtin_processors(self):
        """Load processors from the builtin directory"""
        builtin_dir = os.path.join(os.path.dirname(__file__), "builtin")
        self._load_processors_from_directory(builtin_dir)

    def load_custom_processors(self):
        """Load processors from the custom directory"""
        custom_dir = os.path.join(os.path.dirname(__file__), "custom")
        if not os.path.exists(custom_dir):
            os.makedirs(custom_dir)
        self._load_processors_from_directory(custom_dir)

    def _load_processors_from_directory(self, directory: str):
        """Load processor modules from a directory"""
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
                        
                        for _, obj in inspect.getmembers(module):
                            if (inspect.isclass(obj) and 
                                issubclass(obj, ProcessorBase) and 
                                obj != ProcessorBase):
                                self.register_processor(obj())
                except Exception as e:
                    print(f"Error loading processor {filename}: {e}")

    def register_processor(self, processor: ProcessorBase):
        """Register a new processor"""
        self.processors[processor.name] = processor

    def get_processor(self, name: str) -> ProcessorBase:
        """Get a processor by name"""
        return self.processors.get(name)

    def get_all_processors(self) -> Dict[str, ProcessorBase]:
        """Get all registered processors"""
        return self.processors.copy()
