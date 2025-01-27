#/InterfaceBuilder.py
import flet as ft
from typing import List

from interface.elements.SearchBar import SearchBar
from interface.elements.DynamicConfigContainer import DynamicConfigContainer
from interface.elements.results_panel import ResultsPanel
from interface.elements.processing_panel import ProcessingPanel

from data.ResultQueueManager import ResultQueueManager
from processor.manager import ProcessorManager
from page_manager import PageManager
from console import DHConsole
from processor_logic import *


class DogHouseUI:
    def __init__(self):
        self._page_manager = PageManager()
        self._init_core_components()
        self._init_ui_elements()
        self._init_layout_containers()

    def _init_core_components(self):
        """Initialize core application components."""
        self.queue_manager = ResultQueueManager()
        self.console = DHConsole()
        self.search_bar = SearchBar()

    def _init_ui_elements(self):
        """Initialize main UI elements."""
        self.resultsPanel = ResultsPanel()
        self.processingPanel = ProcessingPanel()
        self.proc_config = DynamicConfigContainer()

    def _init_layout_containers(self):
        """Initialize layout containers and structure."""
        # Control rows
        self.results_controls = ft.Row(
            controls=[],
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True
        )
        self.results_controls.controls = self.resultsPanel.get_controls()
        self.processing_controls = ft.Row(
            controls=[],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Control containers
        self.results_controls_container = ft.Container(
            content=self.results_controls,
            bgcolor=ft.Colors.ON_TERTIARY,
            height=60,
            border_radius=5,
            padding= ft.Padding(20, 5, 20, 5)
        )
        self.processing_controls_container = ft.Container(
            bgcolor=ft.Colors.ON_TERTIARY,
            height=60,
            border_radius=5,
            padding= ft.Padding(20, 5, 20, 5)
        )

        # Main layout columns
        self.results_column = ft.Column(expand=True, controls=[])
        self.processing_column = ft.Column(expand=True, controls=[])
        self.work_row = ft.Row(expand=True, controls=[])

    def _setup_layouts(self):
        """Setup the main layout structure."""
        self.results_column.controls = [
            self.resultsPanel,
            self.results_controls_container,
            self.console.get_console()
        ]

        self.processing_column.controls = [
            self.processingPanel,
            self.processing_controls_container,
            self.proc_config
        ]

        self.work_row.controls = [
            self.results_column,
            self.processing_column
        ]

    def _setup_processing_controls(self):
        """Setup the controls for the processing section."""
        processors = self._get_available_processors()
        self.processingPanel.set_processors(processors)
        self.processingPanel.bind_config(self.proc_config)

        self.processing_controls.controls = self.processingPanel.get_controls()
        self.processing_controls_container.content = self.processing_controls

    def _get_available_processors(self) -> List[str]:
        """Get list of available processors."""
        processor_manager = ProcessorManager()
        return [
            processor.name
            for processor in processor_manager.get_all_processors().values()
        ]

    def _configure_page(self):
        """Configure the main page settings."""
        page = self._page_manager.get_page()
        page.title = "Dog House"
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20

        page.window.min_width = 800
        page.window.min_height = 600
        page.window.width = 1200
        page.window.height = 800

    def _link_queues(self):
        """Link queues with their respective lists."""
        self.queue_manager.get_results_queue().link_list(self.resultsPanel.get_list())
        self.queue_manager.get_proc_queue().link_list(self.processingPanel.get_list())

    def build(self):
        """Build and display the UI."""
        try:
            page = self._page_manager.get_page()
            self._configure_page()
            self._setup_layouts()
            self._setup_processing_controls()

            page.add(self.search_bar)
            page.add(self.work_row)

            self._link_queues()
            page.update()

            self.console.print("UI initialized successfully")

        except Exception as ex:
            print(f"Error building UI: {str(ex)}")
            raise


def BuildUI():
    """Entry point for building the UI."""
    try:
        ui = DogHouseUI()
        ui.build()
    except Exception as ex:
        print(f"Failed to build UI: {str(ex)}")
        raise
