# logic.py
import flet as ft
from pathlib import Path
from typing import Callable
from interface.elements.ExpandableTiles import ExpandableListTile
from data.ResultQueueManager import ResultQueueManager
from data.json_storage import JsonStorageManager
from page_manager import PageManager

class LogicManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        self.page_manager = PageManager()
        self.queue_manager = ResultQueueManager()
        self.storage_manager = JsonStorageManager(Path("saved_results"), self.queue_manager.console)
        
    def clear_duplicates(self, e):
        self.queue_manager.clear_duplicates()
        self.page_manager.get_page().update()
        
    def clear_seen(self, e):
        self.queue_manager.clear_seen()
        self.page_manager.get_page().update()

    def select_all_results(self, e):
        self.queue_manager.select_all_results()
        self.page_manager.get_page().update()

    def deselect_all_results(self, e):
        queue = self.queue_manager.deselect_all_results()
        if queue and queue.attached_list:
            for item in queue.attached_list.items:
                if isinstance(item, ExpandableListTile):
                    item.checkbox.value = False
        self.page_manager.get_page().update()

    def clear_results(self, e):
        self.queue_manager.clear_results()
        self.page_manager.get_page().update()

    def move_to_processing(self, e):
        proc_results, results = self.queue_manager.move_to_processing()
        
        proc_queue = self.queue_manager.get_proc_queue()
        if proc_queue.attached_list:
            proc_queue.sync_list()
            proc_queue.attached_list.set_trailing_all("URL")
        
        results_queue = self.queue_manager.get_results_queue()
        if results_queue.attached_list:
            results_queue.sync_list()
            
        self.page_manager.get_page().update()

    def remove_processed_items(self, e):
        self.queue_manager.remove_processed_items()
        self.queue_manager.get_proc_queue().sync_list()
        self.page_manager.get_page().update()

    def clear_processing(self, e):
        self.queue_manager.clear_processing()
        self.page_manager.get_page().update()

    def remove_failed_items(self, e):
        self.queue_manager.remove_failed_items()
        self.queue_manager.get_proc_queue().sync_list()
        self.page_manager.get_page().update()

    def save_results_json(self, e):
        results = self.queue_manager.get_results_queue().results
        self.storage_manager.save_to_json(results, "results")

    def save_processing_json(self, e):
        results = self.queue_manager.get_proc_queue().results
        self.storage_manager.save_to_json(results, "processing")

    def load_results_json(self, e):
        self.queue_manager.console.print("Loading results from JSON...")
        
        async def on_file_picked(e: ft.FilePickerResultEvent):
            if not e.files or not e.files[0]:
                return
                
            results = self.storage_manager.load_from_json(Path(e.files[0].path))
            if results:
                queue = self.queue_manager.get_results_queue()
                queue.clear_results()
                queue.add_results(results)
                self.page_manager.get_page().update()

        file_picker = ft.FilePicker(on_result=on_file_picked)
        self.page_manager.get_page().overlay.append(file_picker)
        self.page_manager.get_page().update()
        file_picker.pick_files()
