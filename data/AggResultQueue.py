# data/AggResultQueue.py
from typing import List, Optional
from data.Models import AggResult
from interface.elements.ExpandableTiles import ExpandableListTile, DynamicExpandableList
from data.db_manager import DBManager

class AggResultQueue:
    def __init__(self, purpose):
        self.purpose = purpose
        self.attached_list = None
        self.results: List[AggResult] = []
        self.db = DBManager()

    def add_result(self, result: AggResult):
        """Add a single result and sync if list is attached."""
        isUnseen = self.db.add_if_original(result.ip, int(result.port))
        new_result = AggResult(
            ip=result.ip,
            port=result.port,
            service=result.service,
            location=result.location,
            asn=result.asn,
            banner=result.banner,
            domain=result.domain,
            date=result.date,
            extra=result.extra,
            isUnseen=isUnseen
        )
        setattr(new_result, 'isSelected', False)
        self.results.append(new_result)
        self._sync_if_attached()

    def add_results(self, results: List[AggResult]):
        """Add multiple results and sync if list is attached."""
        for result in results:
            self.add_result(result)  # Use add_result to ensure fresh copies

    def get_result_by_index(self, index: int) -> Optional[AggResult]:
        """Safely get result by index."""
        return self.results[index] if 0 <= index < len(self.results) else None

    def select_all(self):
        """Select all results and sync UI if attached."""
        for result in self.results:
            setattr(result, 'isSelected', True)
        if self.attached_list:
            try:
                self.attached_list.select_all()
            except AssertionError:
                pass  # Ignore if list is not yet mounted

    def clear_results(self):
        """Clear all results and sync UI if attached."""
        self.results = []
        self._sync_if_attached()

    def link_list(self, attached_list: 'DynamicExpandableList'):
        """Link an expandable list."""
        self.attached_list = attached_list
        # Don't immediately sync - let the UI control handle its own mounting

    def sync_list(self):
        if not self.attached_list:
            return
        try:
            trailing = "URL" if self.purpose == "PROC" else "CHECKBOX"
            
            new_items = []
            for i, result in enumerate(self.results):
                details = self._format_result_details(result)
                title = f"{result.ip}:{result.port}"
                if getattr(result, 'message', None):
                    title += f" [Status]: {result.message}"
 
                bgColor = "#37414f" if (not result.isUnseen and self.purpose != "PROC") else getattr(result, 'color', None)                   
                expandable_tile = ExpandableListTile(title, expanded_content=details, bgcolor=bgColor)
                expandable_tile.queue_index = i
                expandable_tile.checkbox.value = getattr(result, 'isSelected', False)
                expandable_tile.parent_queue = self
                expandable_tile.set_trailing(trailing)
                new_items.append(expandable_tile)
            
            self.attached_list.items = new_items
            self.attached_list.items_column.controls = new_items
            if new_items:
                self.attached_list.content.content = self.attached_list.items_column
            else:
                self.attached_list.content.content = self.attached_list.empty_state
                
            self.attached_list._safe_update()
                
        except Exception as e:
            import traceback
            print(f"Failed to sync list: {traceback.format_exc()}")

    def _format_result_details(self, result: AggResult) -> str:
        """Format result details for display."""
        details = []
        for key, value in result.__dict__.items():
            if value not in (None, ""):
                details.append(f"{key}: {value}")
        return "\n".join(details)

    def _sync_if_attached(self):
        """Helper method to sync UI if list is attached."""
        if self.attached_list:
            self.sync_list()

    def get_selected_results(self) -> List[AggResult]:
        """Get all selected results."""
        return [result for result in self.results if getattr(result, 'isSelected', False)]
    
    def remove_result(self, result: AggResult):
        """
        Remove a specific result from the queue and sync if list is attached.
        
        Args:
            result (AggResult): The result object to remove
            
        Returns:
            bool: True if result was found and removed, False otherwise
        """
        try:
            self.results.remove(result)
            self._sync_if_attached()
            return True
        except ValueError:
            for i, existing_result in enumerate(self.results):
                if (existing_result.ip == result.ip and 
                    existing_result.port == result.port):
                    del self.results[i]
                    self._sync_if_attached()
                    return True
        
        if self.attached_list and len(self.results) == 0:
            try:
                self.attached_list.content.content = self.attached_list.empty_state
                self.attached_list._safe_update()
            except Exception as e:
                import traceback
                print(f"Failed to update empty state: {traceback.format_exc()}")
        
        return False
    
    def clear_duplicates(self):
        """
        Remove duplicate results that have matching IP:port combinations.
        Keeps the first occurrence of each unique IP:port combination.
        
        Returns:
            int: Number of duplicates removed
        """
        seen = set()
        unique_results = []
        duplicates_removed = 0
        
        for result in self.results:
            identifier = f"{result.ip}:{result.port}"
            
            if identifier not in seen:
                seen.add(identifier)
                unique_results.append(result)
            else:
                duplicates_removed += 1
        
        if duplicates_removed > 0:
            self.results = unique_results
            self._sync_if_attached()
            
            if not unique_results and self.attached_list:
                try:
                    self.attached_list.content.content = self.attached_list.empty_state
                    self.attached_list._safe_update()
                except Exception as e:
                    import traceback
                    print(f"Failed to update empty state: {traceback.format_exc()}")
        
        return duplicates_removed
    
    def remove_all_seen(self):
        """
        Remove all results that have been seen in previous searches.
        Uses the isUnseen attribute to determine if a result is new.
        
        Returns:
            int: Number of seen results removed
        """
        removed_count = 0
        unseen_results = []
        
        for result in self.results:
            if getattr(result, 'isUnseen', False):
                unseen_results.append(result)
            else:
                removed_count += 1
        
        if removed_count > 0:
            self.results = unseen_results
            self._sync_if_attached()
            
            if not unseen_results and self.attached_list:
                try:
                    self.attached_list.content.content = self.attached_list.empty_state
                    self.attached_list._safe_update()
                except Exception as e:
                    import traceback
                    print(f"Failed to update empty state: {traceback.format_exc()}")
        
        return removed_count