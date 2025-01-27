from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type


@dataclass
class ProcessingResult:
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    color: str = "red"

@dataclass 
class ConfigProperty:
    name: str
    type: Type
    default: Any
    description: str
    required: bool = False


class ProcessorBase(ABC):
    """Base class for all processors"""

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize the processor with optional configuration.
        :param config: Configuration dictionary to initialize the processor.
        """
        self._validate_config_properties()
        defaults = self.get_config_defaults()
        self.config = defaults | (config or {})

    @property
    def config_properties(self) -> list[ConfigProperty]:
        """Override this method to return a list of config properties"""
        return []
    def get_config_defaults(self) -> Dict[str, Any]:
        """Returns a dictionary of default values for all config properties"""
        return {prop.name: prop.default for prop in self.config_properties}

    def _validate_config_properties(self) -> None:
        """Validate that all config properties have unique names"""
        seen_names = set()
        for prop in self.config_properties:
            if prop.name in seen_names:
                raise ValueError(f"Duplicate config property name: {prop.name}")
            seen_names.add(prop.name)

    def get_config_values(self, name: str, target: Optional[dict] = None) -> Any:
        """
        Get a configuration value, checking target dict first, then config, then defaults.
        :param name: Name of the config property
        :return: The configuration value
        """
        if target and name in target:
            return target[name]
        return self.config.get(name, self.get_config_defaults().get(name))
    
    def get_all_config_values(self) -> Dict[str, Any]:
        return {prop.name: self.get_config_values(prop.name) for prop in self.config_properties}
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the processor shown in UI"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the processor does"""
        pass

    @abstractmethod
    async def process(self, target: dict) -> ProcessingResult:
        """Process a single target"""
        pass
