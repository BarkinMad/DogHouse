import socket
from processor.base import ProcessorBase, ProcessingResult, ConfigProperty


class PortKnocker(ProcessorBase):
    @property
    def name(self) -> str:
        return "Port Knocker"

    @property
    def description(self) -> str:
        return "Knocks on a port to see if it's reachable."

    @property
    def config_properties(self) -> list[ConfigProperty]:
        return []

    async def process(self, target: dict) -> ProcessingResult:
        ip = target.get("ip")
        port = target.get("port")

        if not ip or not port:
            return ProcessingResult(
                success=False,
                message="Target must include 'ip' and 'port'.",
                details=target,
                color="red"
            )

        try:
            # Attempt to connect to the specified IP and port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)  # Set a timeout for the connection attempt
                result = sock.connect_ex((ip, int(port)))

                if result == 0:
                    return ProcessingResult(
                        success=True,
                        message=f"Knocked on port {port} at {ip}: It's open!",
                        details={"ip": ip, "port": port},
                        color="green"
                    )
                else:
                    return ProcessingResult(
                        success=False,
                        message=f"Knocked on port {port} at {ip}: No response (closed).",
                        details={"ip": ip, "port": port},
                        color="red"
                    )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error while knocking on port {port} at {ip}: {str(e)}",
                details={"ip": ip, "port": port, "error": str(e)},
                color="red"
            )
