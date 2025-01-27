import flet as ft
import asyncio
import threading
from typing import List, Dict, Any
from processor.base import ProcessorBase
from processor.manager import ProcessorManager
from data.ResultQueueManager import ResultQueueManager
from console import DHConsole
from page_manager import PageManager

class ProcessorLogicManager:
    def __init__(self):
        self._page_manager = PageManager()
        self.console = DHConsole()
        self.processor_manager = ProcessorManager()
        self.is_processing = False
        self.current_processor = None
        self.on_processor_changed = self._bind_handler(self._on_processor_changed)
        self.start_processor = self._bind_handler(self._start_processor)
        self.stop_processor = self._bind_handler(self._stop_processor)

    def _bind_handler(self, handler):
        """Helper method to bind event handlers properly."""
        def wrapped(e, *additional_args):
            return handler(e, *additional_args)
        return wrapped

    def _on_processor_changed(self, e, config_container=None):
        """Handle processor selection change"""
        try:
            processor_name = e.data
            self.console.print(f"Processor set to: d[<f=ffffff, b>, <{processor_name}>]")
            
            
            processor = self.processor_manager.get_processor(processor_name)
            print(f"processor: {processor}")
            if not config_container:
                config_container = self._page_manager.get_page().get_control("processor_config")
            
            if processor and config_container:
                self._build_config_ui(processor, config_container)
                self._page_manager.get_page().update()
                
        except Exception as ex:
            self.console.print(f"Error changing processor: {ex}", "error")

    def _build_config_ui(self, processor: ProcessorBase, container: ft.Container):
        """Build configuration UI for selected processor"""
        try:
            container.content_list.controls.clear()
            
            
            container.content_list.controls.append(
                ft.Row([ft.Text(processor.description, size=14, color=ft.Colors.GREY_400)])
            )
            
            
            for prop in processor.config_properties:
                control = self._create_config_control(prop)
                if control:
                    container.content_list.controls.append(
                        ft.Row(
                            controls=[
                                ft.Text(f"{prop.name} ({prop.type.__name__})", expand=1),
                                control
                            ],
                            spacing=0
                        )
                    )
            
            container.update()
            
        except Exception as ex:
            self.console.print(f"Error building config UI: {ex}", "error")
            raise

    def _create_config_control(self, prop):
        """Create appropriate control for config property type"""
        try:
            if prop.type == bool:
                return ft.Checkbox(
                    value=prop.default,
                    tooltip=prop.description
                )
            elif prop.type in (int, float):
                return ft.TextField(
                    value=str(prop.default),
                    tooltip=prop.description,
                    input_filter=ft.NumbersOnlyInputFilter()
                )
            else:
                return ft.TextField(
                    value=str(prop.default),
                    tooltip=prop.description
                )
        except Exception as ex:
            self.console.print(f"Error creating config control: {ex}", "error")
            return None

    def _extract_config_values(self, config_container: ft.Container) -> Dict[str, Any]:
        """Extract configuration values from UI controls"""
        config = {}
        try:
            for row in config_container.content_list.controls[1:]:  
                if isinstance(row, ft.Row) and len(row.controls) == 2:
                    name = row.controls[0].value.split(" (")[0]
                    control = row.controls[1]
                    
                    if isinstance(control, ft.Checkbox):
                        config[name] = control.value
                    else:
                        config[name] = control.value
                        
            return config
            
        except Exception as ex:
            self.console.print(f"Error extracting config values: {ex}", "error")
            raise
    async def _process_items(self, processor: ProcessorBase, items: List[ft.Control],
                            config: Dict[str, Any]):
        queue_manager = ResultQueueManager()
        proc_queue = queue_manager.get_proc_queue()
        
        idx = 1
        for result in proc_queue.results:
            if not self.is_processing:
                self.console.print("Processing interrupted by user")
                break

            try:
                
                setattr(result, 'processing', True)
                if proc_queue.attached_list and idx - 1 < len(proc_queue.attached_list.items):
                    list_item = proc_queue.attached_list.items[idx - 1]
                    list_item.content.controls[0].trailing = ft.ProgressRing(width=16, height=16)
                    list_item.update()
                
                process_result = await processor.process({
                    "ip": result.ip,
                    "port": result.port,
                    **config
                })
                
                setattr(result, 'processed', process_result.success)
                setattr(result, 'failed', not process_result.success)
                setattr(result, 'processing', False)
                setattr(result, 'message', process_result.message)
                setattr(result, 'details', process_result.details)
                setattr(result, 'color', process_result.color)
                
                
                if proc_queue.attached_list and idx - 1 < len(proc_queue.attached_list.items):
                    list_item = proc_queue.attached_list.items[idx - 1]
                    
                    list_item.bgcolor = process_result.color
                    list_item.content.bgcolor = process_result.color
                    list_item.content.controls[0].bgcolor = process_result.color 
                    list_item.content.controls[0].trailing = list_item.checkbox
                    list_item.update()
                
                self.console.print(f"[{processor.name}] {process_result.message}")
                
            except Exception as ex:
                self.console.print(f"Error processing item {idx}: {ex}", "error")
                setattr(result, 'failed', True)
                setattr(result, 'processing', False)
                setattr(result, 'color', 'red')
                
                if proc_queue.attached_list and idx - 1 < len(proc_queue.attached_list.items):
                    list_item = proc_queue.attached_list.items[idx - 1]
                    list_item.content.controls[0].trailing = list_item.checkbox
                    list_item.update()
            
            finally:
                proc_queue.sync_list()
                idx += 1
    def _start_processor(self, e, processor_name, config_container, proc_list):
        """Start processing items"""
        if self.is_processing:
            self.stop_processor(e)
            return
            
        try:
            
            if not processor_name:
                self.console.print("No processor selected")
                return
                    
            processor = self.processor_manager.get_processor(processor_name)
            if not processor:
                self.console.print(f"Processor '{processor_name}' not found")
                return
                    
            
            if not config_container:
                self.console.print("Configuration container not found")
                return
                    
            try:
                config = self._extract_config_values(config_container)
            except Exception as ex:
                self.console.print(f"Error extracting config values: {ex}", "error")
                return
                    
            
            if not proc_list or not proc_list.items:
                self.console.print("No items to process")
                return
                    
            
            self.is_processing = True
            e.control.text = "Stop"
            self._page_manager.get_page().update()

            
            async def process_async():
                try:
                    await self._process_items(processor, proc_list.items, config)
                finally:
                    self.is_processing = False
                    e.control.text = "Process"
                    self._page_manager.get_page().update()
                    
            
            self.console.print(f"Starting processing with '{processor.name}' for {len(proc_list.items)} items")
            threading.Thread(target=lambda: asyncio.run(process_async())).start()
                
        except Exception as ex:
            self.console.print(f"Error starting processor: {ex}", "error")
            self.is_processing = False
            e.control.text = "Process"
            self._page_manager.get_page().update()

    def _stop_processor(self, e):
        """Stop current processing"""
        try:
            self.is_processing = False
            e.control.text = "Process"
            self._page_manager.get_page().update()
            self.console.print("Processing stopped by user")
        except Exception as ex:
            self.console.print(f"Error stopping processor: {ex}", "error")

processor_logic = ProcessorLogicManager()
on_processor_changed = processor_logic.on_processor_changed
start_processor = processor_logic.start_processor
stop_processor = processor_logic.stop_processor