import base64
import requests
from typing import List, Dict, Any
import flet as ft
from plugins.base import PluginBase, FletControlType, FletControlConfig
from plugins.manager import PluginManager
from data.AggResultQueue import AggResult

class HunterPlugin(PluginBase):
    """Hunter Plugin for querying the Hunter API"""
    
    @property
    def name(self) -> str:
        return "Hunter"
    
    @property
    def description(self) -> str:
        return "A plugin to search for IP and port information using the Hunter API."
    
    @property
    def requires_api_key(self) -> bool:
        return True
    
    def get_config_fields(self) -> Dict[str, Dict[str, Any]]:
        return {
            "api_key": {
                "type": "string",
                "label": "Hunter API Key",
                "default": "",
                "required": True
            }
        }

    def get_ui_controls(self) -> List[FletControlConfig]:
        """Define the UI controls for the Hunter plugin"""
        return [
            FletControlConfig(
                control_type=FletControlType.DATEPICKER,
                id="start_date",
                label="Start Date",
                placeholder="YYYY-MM-DD",
                width=200,
                tooltip="Start date for search range"
            ),
            FletControlConfig(
                control_type=FletControlType.DATEPICKER,
                id="end_date",
                label="End Date",
                placeholder="YYYY-MM-DD",
                width=200,
                tooltip="End date for search range"
            ),
            FletControlConfig(
                control_type=FletControlType.DROPDOWN,
                id="page_size",
                label="Results per page",
                options=["10", "20", "50", "100", "1000"],
                default_value="10",
                width=150
            ),
            FletControlConfig(
                control_type=FletControlType.TEXTFIELD,
                id="page_number",
                label="Page Number",
                placeholder="1",
                default_value="1",
                width=150
            )
        ]

    def handle_control_event(self, control_id: str, event_data: Any, page: ft.Page) -> Any:
        """Handle UI control events"""
        # Get current values of controls for search configuration
        control_values = {
            "start_date": page.get_control("start_date").value,
            "end_date": page.get_control("end_date").value,
            "page_size": int(page.get_control("page_size").value),
            "page_number": int(page.get_control("page_number").value)
        }
        return control_values

    async def search(self, query: str, config: Dict[str, Any] = None) -> List[AggResult]:
        if not config:
            config = {}
            
        plugin_manager = PluginManager()
        api_key = config.get("api_key") or plugin_manager.get_api_key(self.name)
        
        if not api_key:
            raise ValueError("API key is required for the Hunter plugin.")

        encoded_query = base64.urlsafe_b64encode(query.encode("utf-8")).decode("ascii")
        start_date = config.get("start_date", "")
        end_date = config.get("end_date", "")
        page_number = config.get("page_number", 1)
        page_size = config.get("page_size", 10)

        api_url = (
            f"https://api.hunter.how/search?api-key={api_key}&query={encoded_query}"
            f"&page={page_number}&page_size={page_size}&start_time={start_date}&end_time={end_date}"
        )

        response = requests.get(api_url)
        if response.status_code != 200:
            raise Exception(
                f"Error fetching data from Hunter API: {response.status_code} - {response.text}"
            )
            
        data = response.json().get("data", {})
        if data is None:
            raise Exception(
                f"Error fetching data from Hunter API: {response.status_code} - {response.text}"
            )

        raw_results = data.get("list", [])
        return self.format_results(raw_results)

    def format_results(self, raw_results: List[Dict[str, Any]]) -> List[AggResult]:
        formatted_results = []
        for result in raw_results:
            formatted_results.append(AggResult(
                ip=result['ip'],
                port=result['port'],
                domain=result['domain'],
            ))
        return formatted_results

    def validate_api_key(self, api_key: str) -> bool:
        """Validate the provided API key by making a sample request."""
        test_url = f"https://api.hunter.how/search?api-key={api_key}&query=test&page=1&page_size=1"
        response = requests.get(test_url)
        return response.status_code == 200