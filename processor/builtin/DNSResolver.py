import socket
from processor.base import ProcessorBase, ProcessingResult
from typing import Any, Callable

class DNSResolver(ProcessorBase):
    @property
    def name(self) -> str:
        return "DNS Resolver"
    
    @property
    def description(self) -> str:
        return "Resolves a hostname to its IP address to verify DNS resolution."
    
    @property
    def config_properties(self) -> list[str]:
        return []

    async def process(self, target: dict) -> ProcessingResult:
        hostname = target['ip']
        port = target['port']

        if not hostname or not port:
            return ProcessingResult(
                success=False,
                message="Hostname or port not provided.",
                color="red"
            )

        try:
            ip_address = socket.gethostbyname(hostname)
            return ProcessingResult(
                success=True,
                message=f"Resolved {hostname} to {ip_address}.",
                color="green"
            )
        except socket.gaierror as e:
            return ProcessingResult(
                success=False,
                message=f"Failed to resolve {hostname}: {e}",
                details={"hostname": hostname, "error": str(e)},
                color="red"
            )