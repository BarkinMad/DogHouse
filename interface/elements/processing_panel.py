import flet as ft
from interface.elements.ExpandableTiles import DynamicExpandableList
from logic import LogicManager
from processor_logic import start_processor, on_processor_changed
from page_manager import PageManager


class ProcessingPanel(ft.Container):
    def __init__(self):
        super().__init__(expand=True)
        self._page_manager = PageManager()
        self._logic = LogicManager()
        self._list = DynamicExpandableList()
        self._page = None
        self._proc_config = None
        self._init_controls()
        self._bind_controls()

        # Only include the list in the content; controls are handled externally
        self.content = self._list

    def _init_controls(self):
        # Processing buttons
        self._btn_save_json = ft.ElevatedButton(
            text="Save JSON",
            icon=ft.Icons.SAVE,
            tooltip="Save processing list to JSON.",
            expand=True
        )
        self._btn_clear = ft.ElevatedButton(
            text="Clear",
            icon=ft.Icons.DELETE,
            tooltip="Clear the processing list.",
            expand=True
        )
        self._btn_start = ft.ElevatedButton(
            icon=ft.Icons.PLAY_ARROW,
            text="Process",
            tooltip="Start processing selected items.",
            expand=True,
        )
        self._dropdown_processor = ft.Dropdown(
            label="Processor",
            tooltip="Select a processor to use.",
            options=[],
            expand=True,
        )
    def bind_config(self, config):
        self._proc_config = config

    def _bind_controls(self):
        self._btn_save_json.on_click = lambda e: self._logic.save_processing_json(e)
        self._btn_clear.on_click = lambda e: self._logic.clear_processing(e)
        self._dropdown_processor.on_change = lambda e: on_processor_changed(e, self._proc_config)
        self._btn_start.on_click = lambda e: start_processor(
            e, self._dropdown_processor.value, self._proc_config, self._list
        )

    def get_controls(self):
        return [
            self._btn_save_json,
            self._btn_clear,
            self._btn_start,
            self._dropdown_processor
        ]

    def set_processors(self, processors):
        self._dropdown_processor.options = [
            ft.dropdown.Option(key=processor) for processor in processors
        ]

        if self._dropdown_processor.page:
            self._dropdown_processor.update()
        
    def get_list(self):
        return self._list
