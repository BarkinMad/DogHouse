import aiohttp
import base64
from typing import List, Dict, Any, Optional
import flet as ft
from plugins.base import PluginBase, FletControlType, FletControlConfig
from plugins.manager import PluginManager
from data.AggResultQueue import AggResult

class ZoomEyePlugin(PluginBase):
    """ZoomEye API integration plugin for searching internet-connected devices"""
    
    @property
    def name(self) -> str:
        return "ZoomEye"
    
    @property
    def description(self) -> str:
        return "Search for internet-connected devices using the ZoomEye API"
    
    @property
    def version(self) -> str:
        return "2.0.0"
    
    @property
    def requires_api_key(self) -> bool:
        return True
    
    @property
    def max_results(self) -> Optional[int]:
        return 10000  # ZoomEye API limit

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
        """Define the UI controls for the ZoomEye plugin"""
        return [
            FletControlConfig(
                control_type=FletControlType.DROPDOWN,
                id="sub_type",
                label="Data Type",
                options=["v4", "v6", "web"],
                default_value="v4",
                width=150,
                tooltip="Type of data to search for"
            ),
            FletControlConfig(
                control_type=FletControlType.TEXTFIELD,
                id="fields",
                label="Fields",
                placeholder="ip,port,domain,update_time",
                default_value="ip,port,domain,update_time",
                width=300,
                tooltip="Comma-separated fields to return"
            ),
            FletControlConfig(
                control_type=FletControlType.TEXTFIELD,
                id="facets",
                label="Facets",
                placeholder="country,city,port",
                width=300,
                tooltip="Statistical items for grouping results"
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
            ),

        ]

    def handle_control_event(self, control_id: str, event_data: Any, page: ft.Page) -> Any:
        """Handle UI control events"""
        control_values = {
            "sub_type": page.get_control("sub_type").value,
            "fields": page.get_control("fields").value,
            "facets": page.get_control("facets").value,
            "page_size": int(page.get_control("page_size").value),
            "page_number": int(page.get_control("page_number").value),
            "ignore_cache": page.get_control("ignore_cache").value
        }
        return control_values

    def validate_api_key(self, api_key: str) -> bool:
        """Validate ZoomEye API key by making a test request"""
        try:
            api_url = "https://api.zoomeye.ai/v2/search"
            headers = {
                "API-KEY": api_key,
                "content-type": "application/json",
            }
            payload = {
                "qbase64": base64.urlsafe_b64encode(b"port:80").decode("ascii"),
                "page": 1,
                "pagesize": 1,
            }
            response = requests.post(api_url, headers=headers, json=payload)
            return response.status_code == 200
        except Exception:
            return False
        
    async def search(self, query: str, config: Dict[str, Any] = None) -> List[AggResult]:
        """
        Search ZoomEye API for internet-connected devices
        
        Args:
            query: ZoomEye search query
            config: Configuration dictionary containing optional parameters
            
        Returns:
            List of AggResult objects containing found devices
            
        Raises:
            ValueError: If API key is not configured or invalid
            aiohttp.ClientError: If API request fails
        """
        if not config:
            config = {}
            
        plugin_manager = PluginManager()
        api_key = config.get("api_key") or plugin_manager.get_api_key(self.name)
        
        if not api_key:
            raise ValueError("ZoomEye API key is not configured")
            
        encoded_query = base64.urlsafe_b64encode(query.encode("utf-8")).decode("ascii")
        api_url = "https://api.zoomeye.ai/v2/search"
        headers = {
            "API-KEY": api_key,
            "content-type": "application/json",
        }
        
        # Build payload with all supported parameters
        payload = {
            "qbase64": encoded_query,
            "page": config.get("page_number", 1),
            "pagesize": config.get("page_size", 10),
        }
        
        # Add optional parameters if provided
        if config.get("sub_type"):
            payload["sub_type"] = config["sub_type"]
        if config.get("fields"):
            payload["fields"] = config["fields"]
        if config.get("facets"):
            payload["facets"] = config["facets"]

        
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    entries = data.get("data", [])
                    return self.format_results(entries)
                else:
                    error_text = await response.text()
                    raise aiohttp.ClientError(
                        f"ZoomEye API error (status {response.status}): {error_text}"
                    )

    def format_results(self, raw_results: List[Dict[str, Any]]) -> List[AggResult]:
        """Format raw API results into AggResult objects"""
        formatted_results = []
        seen_ips = set()
        
        for entry in raw_results:
            ip = entry.get("ip")
            if ip and ip not in seen_ips:
                seen_ips.add(ip)
                formatted_results.append(AggResult(
                    ip=ip,
                    port=entry.get("port"),
                    domain=entry.get("hostname", [""])[0] if entry.get("hostname") else "",
                    service=entry.get("service", {}).get("name", "unknown"),
                    location=f"{entry.get('geoinfo', {}).get('country', '')}, "
                            f"{entry.get('geoinfo', {}).get('city', '')}".strip(", "),
                    protocol=entry.get("protocol", {}).get("name"),
                    os=entry.get("os"),
                    timestamp=entry.get("timestamp")
                ))
        
        return formatted_results
    
    def validate_query(self, query: str) -> bool:
        """Validate ZoomEye search query"""
        query = query.strip()
        return bool(query) and len(query) >= 3