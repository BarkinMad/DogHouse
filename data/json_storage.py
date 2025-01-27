# storage/json_storage.py
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from data.Models import AggResult
from console import DHConsole


class JsonStorageManager:
    def __init__(self, results_dir: Path, console: DHConsole):
        self.results_dir = results_dir
        self.console = console
        self.results_dir.mkdir(exist_ok=True)

    def save_to_json(self, results: list, prefix: str) -> Optional[Path]:
        if not results:
            self.console.print("No results to save", "warning")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"{prefix}_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump([r.__dict__ for r in results], f, indent=2)

        self.console.print(f"Saved {len(results)} results to {filename}")
        return filename

    def load_from_json(self, file_path: Path) -> List[AggResult]:
        try:
            with open(file_path, 'r') as file:
                results = json.load(file)

            if results:
                clean_results = []
                for r in results:
                    try:
                        result = AggResult(**r)
                        clean_results.append(result)
                    except TypeError:
                        expected_args = set(
                            AggResult.__init__.__code__.co_varnames)
                        filtered_data = {k: v for k,
                                         v in r.items() if k in expected_args}
                        result = AggResult(**filtered_data)
                        clean_results.append(result)

                self.console.print(f"Loaded {len(results)} results")
                return clean_results
            return []
        except Exception as ex:
            self.console.print(
                f"Error loading results from JSON: {ex}", "error")
            return []
