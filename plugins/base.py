from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import flet as ft
import datetime

@dataclass
class SearchResult:
    """Standard format for search results across all plugins"""
    ip: str
    port: int
    service: str
    location: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class FletControlType(Enum):
    """Types of Flet controls that plugins can use"""
    TEXTFIELD = "textfield"
    BUTTON = "button"
    CHECKBOX = "checkbox"
    DATEPICKER = "datepicker"
    DROPDOWN = "dropdown"

@dataclass
class FletControlConfig:
    """Configuration for a Flet control"""
    control_type: FletControlType
    id: str
    label: str
    width: int = 200
    required: bool = False
    default_value: Any = None
    placeholder: str = ""
    disabled: bool = False
    options: Optional[List[str]] = None  # For dropdown
    on_change: Optional[str] = None  # Name of method to call on change
    on_click: Optional[str] = None   # Name of method to call on click
    visible: bool = True
    tooltip: Optional[str] = None
    expand: bool = False
    # Add any other common Flet control properties here

class PluginBase(ABC):
    """Base class for all search plugins"""
   
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the plugin shown in UI"""
        pass
   
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the plugin does"""
        pass
   
    @property
    def version(self) -> str:
        """Plugin version"""
        return "1.0.0"
   
    @property
    def requires_api_key(self) -> bool:
        """Whether this plugin requires an API key"""
        return False
   
    @property
    def max_results(self) -> Optional[int]:
        """Maximum number of results this plugin can return. None for unlimited."""
        return None

    @abstractmethod
    def get_ui_controls(self) -> List[FletControlConfig]:
        """
        Define the Flet controls needed by this plugin
        
        Returns:
            List of FletControlConfig objects defining the interface controls
        """
        pass

    def create_flet_control(self, config: FletControlConfig, page: ft.Page) -> ft.Control:
        """
        Create a Flet control from configuration
        
        Args:
            config: FletControlConfig for the control
            page: Flet page instance for control registration
            
        Returns:
            Flet Control instance
        """
        if config.control_type == FletControlType.TEXTFIELD:
            return ft.TextField(
                label=config.label,
                width=config.width,
                value=config.default_value,
                hint_text=config.placeholder,
                disabled=config.disabled,
                visible=config.visible,
                tooltip=config.tooltip,
                expand=config.expand
            )
            
        elif config.control_type == FletControlType.BUTTON:
            return ft.ElevatedButton(
                text=config.label,
                width=config.width,
                disabled=config.disabled,
                visible=config.visible,
                tooltip=config.tooltip,
                expand=config.expand
            )
            
        elif config.control_type == FletControlType.CHECKBOX:
            return ft.Checkbox(
                label=config.label,
                value=config.default_value or False,
                disabled=config.disabled,
                visible=config.visible,
                tooltip=config.tooltip
            )
            
        elif config.control_type == FletControlType.DROPDOWN:
            return ft.Dropdown(
                label=config.label,
                width=config.width,
                options=[ft.dropdown.Option(opt) for opt in (config.options or [])],
                value=config.default_value,
                disabled=config.disabled,
                visible=config.visible,
                tooltip=config.tooltip,
                expand=config.expand
            )
            
        elif config.control_type == FletControlType.DATEPICKER:
            return ft.TextField(
                label=config.label,
                width=config.width,
                value=datetime.date.today().strftime("%Y-%m-%d"),
                hint_text="YYYY-MM-DD",
                disabled=config.disabled,
                visible=config.visible,
                tooltip=config.tooltip,
                expand=config.expand,
            )
            
        raise ValueError(f"Unsupported control type: {config.control_type}")

    def handle_control_event(self, control_id: str, event_data: Any, page: ft.Page) -> Any:
        """
        Handle control events (e.g. button clicks, value changes)
        
        Args:
            control_id: ID of the control that triggered the event
            event_data: Data associated with the event
            page: Flet page instance
            
        Returns:
            Optional response data
        """
        pass

    def get_config_fields(self) -> Dict[str, Dict[str, Any]]:
        """
        Override to specify configuration fields needed by the plugin
       
        Returns:
            Dict with field names as keys and field properties as values:
            {
                "field_name": {
                    "type": "string|integer|boolean|select",
                    "label": "Human readable label",
                    "default": default_value,
                    "required": True|False,
                    "options": ["option1", "option2"] # Only for type="select"
                }
            }
        """
        return {}
   
    def validate_api_key(self, api_key: str) -> bool:
        """Validate the API key if required"""
        return True
   
    @abstractmethod
    async def search(self, query: str, config: Dict[str, Any] = None) -> List[SearchResult]:
        """Perform search using the plugin"""
        pass
   
    def validate_query(self, query: str) -> bool:
        """Validate search query before execution"""
        return bool(query.strip())
   
    @abstractmethod
    def format_results(self, raw_results: List[Dict[str, Any]]) -> List[SearchResult]:
        """Format raw results into SearchResult objects"""
        pass