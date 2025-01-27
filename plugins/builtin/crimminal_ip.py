import aiohttp
from typing import List, Dict, Any, Optional
import flet as ft
from plugins.base import PluginBase, FletControlType, FletControlConfig
from plugins.manager import PluginManager
from data.AggResultQueue import AggResult

class CriminalIPPlugin(PluginBase):
    """CriminalIP Plugin for querying the CriminalIP API"""

    @property
    def name(self) -> str:
        return "CriminalIP"

    @property
    def description(self) -> str:
        return "A plugin to search for banner information using the CriminalIP API."

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def requires_api_key(self) -> bool:
        return True

    @property
    def max_results(self) -> Optional[int]:
        return 9900  # CriminalIP API limit on offset

    def get_config_fields(self) -> Dict[str, Dict[str, Any]]:
        return {
            "api_key": {
                "type": "string",
                "label": "API Key",
                "required": True,
                "default": "",
            }
        }

    def get_ui_controls(self) -> List[FletControlConfig]:
        """Define the UI controls for the CriminalIP plugin"""
        return [
            FletControlConfig(
                control_type=FletControlType.TEXTFIELD,
                id="offset",
                label="Offset",
                default_value="0",
                width=150,
                tooltip="Starting position in the dataset (increments of 10)"
            ),
        ]

    def handle_control_event(self, control_id: str, event_data: Any, page: ft.Page) -> Any:
        """Handle UI control events"""
        control_values = {
            "offset": int(page.get_control("offset").value),
        }
        return control_values

    def validate_api_key(self, api_key: str) -> bool:
        """Validate the provided API key by making a sample request."""
        test_url = "https://api.criminalip.io/v1/banner/search?query=test&offset=0"
        headers = {"x-api-key": api_key}
        try:
            response = requests.get(test_url, headers=headers)
            return response.status_code == 200
        except Exception:
            return False

    async def search(self, query: str, config: Dict[str, Any] = None) -> List[AggResult]:
        """
        Search CriminalIP API for banner information

        Args:
            query: Search query for the API
            config: Configuration dictionary containing optional parameters

        Returns:
            List of AggResult objects containing found data

        Raises:
            ValueError: If API key is not configured or invalid
            aiohttp.ClientError: If API request fails
        """
        if not config:
            config = {}

        plugin_manager = PluginManager()
        api_key = config.get("api_key") or plugin_manager.get_api_key(self.name)

        if not api_key:
            raise ValueError("CriminalIP API key is not configured")

        api_url = f"https://api.criminalip.io/v1/banner/search?query={query}&offset={config.get('offset', 0)}"
        headers = {"x-api-key": api_key}

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    entries = data.get("data", {}).get("result", [])
                    return self.format_results(entries)
                else:
                    error_text = await response.text()
                    raise aiohttp.ClientError(
                        f"CriminalIP API error (status {response.status}): {error_text}"
                    )

    def format_results(self, raw_results: List[Dict[str, Any]]) -> List[AggResult]:
        """Format raw API results into AggResult objects"""
        formatted_results = []
        for entry in raw_results:
            formatted_results.append(AggResult(
                ip=entry.get("ip_address", ""),
                port=entry.get("open_port_no", 0),
                service=entry.get("product", "unknown"),
                location=f"{entry.get('country', '')}, {entry.get('city', '')}".strip(", "),
                asn=entry.get("org_name", ""),
                banner=entry.get("banner", ""),
                domain=entry.get("hostname", ""),
                date=entry.get("timestamp", ""),
                extra=str({
                    key: value for key, value in entry.items() 
                    if key not in ["ip_address", "open_port_no", "product", "country", "city", "org_name", "banner", "hostname", "timestamp"]
                })
            ))
        return formatted_results

    def validate_query(self, query: str) -> bool:
        """Validate CriminalIP search query"""
        query = query.strip()
        return bool(query) and len(query) >= 3
