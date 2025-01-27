# data/ResultQueueManager.py
from typing import List, Optional, Tuple
from data.AggResultQueue import AggResultQueue, AggResult
from console import DHConsole


class ResultQueueManager:
    _instance = None

    def clear_duplicates(self) -> int:
        """Remove duplicate items from the results queue."""
        try:
            initial_count = len(self.results_queue.results)
            self.results_queue.clear_duplicates()
            removed = initial_count - len(self.results_queue.results)
            self.console.print(f"Removed {removed} duplicate items")
            return removed
        except Exception as ex:
            self.console.print(f"Error clearing duplicates: {ex}", "error")
            return 0

    def clear_seen(self) -> int:
        """Remove all seen items from the results queue."""
        try:
            initial_count = len(self.results_queue.results)
            removed = self.results_queue.remove_all_seen()
            self.console.print(f"Removed {removed} seen items")
            return removed
        except Exception as ex:
            self.console.print(f"Error clearing seen items: {ex}", "error")
            return 0

    def __init__(self):
        if not ResultQueueManager._instance:
            self.results_queue = AggResultQueue(purpose="RES")
            self.proc_queue = AggResultQueue(purpose="PROC")
            self.console = DHConsole()
            ResultQueueManager._instance = self
        else:
            self.results_queue = ResultQueueManager._instance.results_queue
            self.proc_queue = ResultQueueManager._instance.proc_queue
            self.console = ResultQueueManager._instance.console

    def get_results_queue(self) -> AggResultQueue:
        return self.results_queue

    def get_proc_queue(self) -> AggResultQueue:
        return self.proc_queue

    def select_all_results(self) -> None:
        """Select all items in the results queue."""
        try:
            self.results_queue.select_all()
            self.console.print("Selected all results successfully")
        except Exception as ex:
            self.console.print(f"Error selecting all results: {ex}", "error")

    def deselect_all_results(self) -> Optional[AggResultQueue]:
        """Deselect all items in the results queue."""
        try:
            for result in self.results_queue.results:
                setattr(result, 'isSelected', False)
            self.console.print("Deselected all results successfully")
            return self.results_queue
        except Exception as ex:
            self.console.print(f"Error deselecting all results: {ex}", "error")
            return None

    def move_to_processing(self) -> Tuple[List[AggResult], List[AggResult]]:
        """Move selected items from results queue to processing queue."""
        try:
            selected = self.results_queue.get_selected_results()
            if not selected:
                self.console.print("No items selected to move", "warning")
                return [], []

            self.proc_queue.results.extend(selected)
            self.results_queue.results = [
                r for r in self.results_queue.results if r not in selected]

            self.console.print(f"Moved {len(selected)} items to processing")
            return self.proc_queue.results, self.results_queue.results
        except Exception as ex:
            self.console.print(
                f"Error moving items to processing: {ex}", "error")
            return [], []

    def remove_processed_items(self) -> int:
        """Remove processed items from the processing queue."""
        try:
            initial_count = len(self.proc_queue.results)
            self.proc_queue.results = [
                r for r in self.proc_queue.results if not getattr(r, 'processed', False)]
            removed = initial_count - len(self.proc_queue.results)
            self.console.print(f"Removed {removed} processed items")
            return removed
        except Exception as ex:
            self.console.print(
                f"Error removing processed items: {ex}", "error")
            return 0

    def remove_failed_items(self) -> int:
        """Remove failed items from the processing queue."""
        try:
            initial_count = len(self.proc_queue.results)
            self.proc_queue.results = [
                r for r in self.proc_queue.results if not getattr(r, 'failed', False)]
            removed = initial_count - len(self.proc_queue.results)
            self.console.print(f"Removed {removed} failed items")
            return removed
        except Exception as ex:
            self.console.print(f"Error removing failed items: {ex}", "error")
            return 0

    def clear_results(self) -> None:
        """Clear all items from the results queue."""
        try:
            self.results_queue.clear_results()
            self.console.print("Cleared all results successfully")
        except Exception as ex:
            self.console.print(f"Error clearing results: {ex}", "error")

    def clear_processing(self) -> None:
        """Clear all items from the processing queue."""
        try:
            self.proc_queue.clear_results()
            self.console.print("Cleared processing queue successfully")
        except Exception as ex:
            self.console.print(
                f"Error clearing processing queue: {ex}", "error")
