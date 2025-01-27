import base64
import requests
from typing import List, Dict, Any
import flet as ft
from plugins.base import PluginBase, FletControlType, FletControlConfig
from plugins.manager import PluginManager
from data.AggResultQueue import AggResult

class ManualEntry(PluginBase):
    """Manually enter service information without a database"""
    
    @property
    def name(self) -> str:
        return "Manual Entry"
    
    @property
    def description(self) -> str:
        return "A plugin to manually enter service information without querying a database."
    
    @property
    def requires_api_key(self) -> bool:
        return False
    
    def get_config_fields(self) -> Dict[str, Dict[str, Any]]:
        return {
        }

    def get_ui_controls(self) -> List[FletControlConfig]:
        """Define the UI controls for the manual entry plugin"""
        return [
            FletControlConfig(
                control_type=FletControlType.TEXTFIELD,
                id="port",
                label="service port",
                placeholder="service port",
                width=150
            ),
            FletControlConfig(
                control_type=FletControlType.TEXTFIELD,
                id="banner",
                label="service banner",
                placeholder="service banner",
                width=150
            ),
            FletControlConfig(
                control_type=FletControlType.TEXTFIELD,
                id="domain",
                label="host domain",
                placeholder="domain",
                width=150
            )
        ]

    def handle_control_event(self, control_id: str, event_data: Any, page: ft.Page) -> Any:
        """Handle UI control events"""
        control_values = {
            "banner": page.get_control("banner").value,
            "port": page.get_control("port").value,
        }
        return control_values

    async def search(self, query: str, config: Dict[str, Any] = None) -> List[AggResult]:
        if not config:
            raise f"Config is required for manual entry."
        if not query:
            raise "IP is required for manual entry. Use query field."
        if not config.get("port"):
            raise f"Port is required for manual entry."
        host = query
        port = int(config.get("port"))
        banner = config.get("banner", "")
        domain = config.get("domain", "")
        item = {"host": host, "port": port, "banner": banner, "domain": domain}
        return self.format_results([item])
        

    def format_results(self, raw_results: List[Dict[str, Any]]) -> List[AggResult]:
        formatted_results = []
        for result in raw_results:
            formatted_results.append(AggResult(
                ip=result['host'],
                port=result['port'],
                domain=result['domain'],
                banner=result['banner'],
            ))
        return formatted_results

    def validate_api_key(self, api_key: str) -> bool:
        return True