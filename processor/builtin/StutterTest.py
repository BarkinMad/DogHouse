import socket
from time import time
from processor.base import ProcessorBase, ProcessingResult, ConfigProperty
from typing import List


class StutterTester(ProcessorBase):
    @property
    def name(self) -> str:
        return "Stutter Tester"

    @property
    def description(self) -> str:
        return (
            "Measures response times for failed connections to identify potential stealth services or anomalies."
        )

    @property
    def config_properties(self) -> List[ConfigProperty]:
        return [
            ConfigProperty(
                name="timeout",
                type=int,
                default=5,
                description="Connection timeout in seconds.",
            ),
            ConfigProperty(
                name="attempts",
                type=int,
                default=3,
                description="Number of attempts per host.",
            ),
        ]

    async def process(self, target: dict) -> ProcessingResult:
        host = target.get("ip")
        port = int(target.get("port", 80))

        if not host:
            return ProcessingResult(
                success=False,
                message="Target must include 'ip'.",
                details=target,
                color="red",
            )

        timeout = int(self.get_config_values("timeout", target))
        attempts = int(self.get_config_values("attempts", target))
        results = []

        try:
            for attempt in range(1, attempts + 1):
                start_time = time()
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(timeout)
                        sock.connect((host, port))
                except (socket.timeout, socket.error):
                    # Record the time for failed attempts
                    end_time = time()
                    results.append(end_time - start_time)

            # Analyze results
            average_time = sum(results) / len(results) if results else 0
            slow_fail = average_time > timeout / 2  # Arbitrary heuristic for "stuttering"

            if slow_fail:
                return ProcessingResult(
                    success=True,
                    message=f"Host {host}:{port} exhibits stuttering behavior. Average failure time: {average_time:.2f}s.",
                    details={"host": host, "port": port, "attempts": results},
                    color="yellow",
                )
            else:
                return ProcessingResult(
                    success=False,
                    message=f"Host {host}:{port} failed quickly. Average failure time: {average_time:.2f}s.",
                    details={"host": host, "port": port, "attempts": results},
                    color="green",
                )

        except Exception as e:
            return ProcessingResult(
                success=False,
                message=f"Error during stutter test for {host}:{port}: {str(e)}",
                details={"host": host, "port": port, "error": str(e)},
                color="red",
            )
