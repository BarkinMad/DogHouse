# processor/builtin/BearClaw.py
import socket
import random
from processor.base import ProcessorBase, ProcessingResult


class BearClaw(ProcessorBase):
    @property
    def name(self) -> str:
        return "Bear Claw"

    @property
    def description(self) -> str:
        return (
            "Attempts to identify honeypots by sending unconventional traffic and analyzing responses."
        )
    
    @property
    def config_properties(self) -> list[str]:
        return []

    async def process(self, target: dict) -> ProcessingResult:
        ip = target.get("ip")
        port = target.get("port", 80)  # Default to HTTP port if none provided

        if not ip:
            return ProcessingResult(
                success=False,
                message="Target must include 'ip'.",
                details=target,
                color="red",
            )

        try:
            # Generate random unusual traffic
            random_string = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=12))
            payload = f"GET /{random_string} HTTP/1.1\r\nHost: {ip}\r\n\r\n"

            # Attempt to connect to the target
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect((ip, int(port)))
                sock.sendall(payload.encode("utf-8"))

                response = sock.recv(1024).decode("utf-8", errors="ignore")

            # Simple honeypot detection heuristics
            if "honeypot" in response.lower() or "capture" in response.lower():
                return ProcessingResult(
                    success=True,
                    message=f"Honeypot detected on {ip}:{port}.",
                    details={"ip": ip, "port": port, "response": response},
                    color="red",
                )

            if len(response) < 20:  # Honeypots may return minimal or unrealistic responses
                return ProcessingResult(
                    success=True,
                    message=f"Potential honeypot behavior detected on {ip}:{port}. Response too short.",
                    details={"ip": ip, "port": port, "response": response},
                    color="yellow",
                )

            # If no suspicious behavior is detected
            return ProcessingResult(
                success=False,
                message=f"No honeypot behavior detected on {ip}:{port}.",
                details={"ip": ip, "port": port, "response": response},
                color="green",
            )

        except (socket.timeout, socket.error) as e:
            return ProcessingResult(
                success=False,
                message=f"Failed to connect to {ip}:{port}: {str(e)}",
                details={"ip": ip, "port": port, "error": str(e)},
                color="red",
            )
