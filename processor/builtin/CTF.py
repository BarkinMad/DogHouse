import socket
from typing import List
from processor.base import ProcessorBase, ProcessingResult, ConfigProperty


class CaptureTheFlag(ProcessorBase):
    @property
    def name(self) -> str:
        return "Capture The Flag"

    @property
    def description(self) -> str:
        return (
            "Retrieves banners for common services (HTTP, FTP, SMTP, POP3) to identify service versions and configurations."
        )

    @property
    def config_properties(self) -> List[ConfigProperty]:
        return [
            ConfigProperty(
                name="timeout",
                type=int,
                default=5,
                description="Timeout for banner grabbing in seconds."
            ),
            ConfigProperty(
                name="force_service",
                type=str,
                default="",
                description="Force a specific service type (HTTP, FTP, SMTP, POP3) regardless of port."
            )
        ]

    async def process(self, target: dict) -> ProcessingResult:
        host = target.get("ip")
        port = int(target.get("port"))

        if not host or not port:
            return ProcessingResult(
                success=False,
                message="Target must include 'ip' and 'port'.",
                details=target,
                color="red",
            )

        timeout = self.get_config_values("timeout", target)

        # Service-specific payloads or interactions
        banners = {}
        service_ports = {
            80: "HTTP",
            21: "FTP",
            25: "SMTP",
            110: "POP3",
        }
        forced_service = self.get_config_values("force_service", target)
        if forced_service:
            service_name = forced_service
        else:
            service_name = service_ports.get(port, "Unknown Service")

        try:
            service_name = service_ports.get(port, "Unknown Service")

            # Create a socket connection
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((host, port))

                if port == 80:
                    # Send an HTTP GET request
                    sock.sendall(b"GET / HTTP/1.1\r\nHost: \r\n\r\n")
                elif port == 21 or port == 25 or port == 110:
                    # Let the service respond with its default banner
                    pass

                # Receive the banner
                response = sock.recv(1024).decode("utf-8", errors="ignore")
                banners[service_name] = response

            # Process the result
            if banners:
                return ProcessingResult(
                    success=True,
                    message=f"Banner retrieved for {host}:{port}. {banners}",
                    details={"banners": banners},
                    color="green",
                )
            else:
                return ProcessingResult(
                    success=False,
                    message=f"No banner received from {host}:{port}.",
                    details={},
                    color="yellow",
                )

        except socket.timeout:
            return ProcessingResult(
                success=False,
                message=f"Connection to {host}:{port} timed out.",
                details={},
                color="red",
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error during banner grab for {host}:{port}: {str(e)}",
                details={"error": str(e)},
                color="red",
            )
