import flet as ft
from plugins.manager import PluginManager
from data.ResultQueueManager import ResultQueueManager
from console import DHConsole
from data.MockData import MOCK_DATA

class SearchBar(ft.Container):
    def __init__(self):
        super().__init__()
        self.console = DHConsole()
        self.pluginManager = PluginManager()
        self.current_plugin = None  # Track current selected plugin

        # elements
        self.border_radius = 5
        self.mainCol = ft.Column()
        self.searchRow = ft.Row()
        self.controlRow = ft.Row()
        self.searchButton = ft.ElevatedButton("Search", on_click=self.search)
        self.searchTextField = ft.TextField(label="Search", expand=True)
        self.testModeCheck = ft.Checkbox(label="Test Mode", value=False)
        self.progressSpinner = ft.ProgressRing(scale=0.75, visible=False, color=ft.Colors.WHITE)
        self.dbDropdown = ft.Dropdown(
            label="Database",
            options=[ft.dropdown.Option(name) for name in self.pluginManager.get_all_plugins().keys()],
            on_change=self.handle_plugin_change
        )

        # layout
        self.content = self.mainCol
        self.searchContainer = ft.Container(content=self.searchRow, padding=0)
        self.controlContainer = ft.Container(content=self.controlRow, padding=0)
        self.mainCol.controls = [self.searchContainer, self.controlContainer]
        self.searchRow.controls = [self.dbDropdown, self.searchTextField, self.searchButton, self.progressSpinner, self.testModeCheck]
        self.controlRow.controls = [ft.Text("Select a database to start sniffing")]

        # style
        self.bgcolor = ft.Colors.SECONDARY_CONTAINER
        self.searchContainer.bgcolor = ft.Colors.SECONDARY_CONTAINER
        self.searchContainer.padding = ft.padding.all(10)
        self.controlContainer.bgcolor = ft.Colors.ON_SECONDARY
        self.controlContainer.padding = ft.padding.all(5)

        # Store references to plugin controls
        self.plugin_controls = {}

    def handle_plugin_change(self, e):
        """Handle plugin selection change"""
        dbName = e.control.value
        self.set_db(dbName)
        
        # Clear existing plugin controls
        self.controlRow.controls.clear()
        self.plugin_controls.clear()
        
        plugin = self.pluginManager.get_plugin(dbName)
        if plugin:
            self.current_plugin = plugin
            control_configs = plugin.get_ui_controls()
            if control_configs:
                for config in control_configs:
                    control = plugin.create_flet_control(config, self.page)
                    self.plugin_controls[config.id] = control
                    if config.on_change:
                        control.on_change = lambda e, cid=config.id: self.handle_control_event(cid, e)
                    if config.on_click:
                        control.on_click = lambda e, cid=config.id: self.handle_control_event(cid, e)
                self.controlRow.controls = list(self.plugin_controls.values())
            else:
                self.controlRow.controls = [ft.Text("No additional options available")]
        else:
            self.controlRow.controls = [ft.Text("Select a database to start sniffing")]
        
        self.update()

    def handle_control_event(self, control_id: str, e):
        """Handle events from plugin controls"""
        if self.current_plugin:
            result = self.current_plugin.handle_control_event(control_id, e, self.page)
            if result:
                self.plugin_control_values = result

    async def search(self, e):
        """Execute search with current plugin and control values"""
        query = self.searchTextField.value

        if self.testModeCheck.value:
            self.console.print("Loading mock data...")
            self.handle_search_results(MOCK_DATA)
            return
        elif not self.current_plugin:
            self.console.print("d[<f=ff002b>, <Can not search, no plugin selected>]")
            return
        elif not query:
            self.console.print("d[<f=ff002b>, <Can not search, no query provided>]")
            return

        config = {}
        for control_id, control in self.plugin_controls.items():
            config[control_id] = control.value

        try:
            self.console.print(f"Searching {self.current_plugin.name} with query: {query}...")
            self.set_progress_spinner(True)
            results = await self.current_plugin.search(query, config)
            self.handle_search_results(results)
            self.set_progress_spinner(False)
        except Exception as ex:
            self.set_progress_spinner(False)
            self.console.print(f"Error searching {self.current_plugin.name}: {str(ex)}")
            print(f"Search error: {str(ex)}")

    def set_progress_spinner(self, visible):
        self.progressSpinner.visible = visible
        self.update()

    def handle_search_results(self, results):
        self.console.print(f"Found {len(results)} results")
        queueManager = ResultQueueManager()
        resultsQueue = queueManager.get_results_queue()
        resultsQueue.add_results(results)
        resultsQueue.sync_list()

    def set_db(self, dbName: str):
        setattr(self.searchTextField, "label", f"Search {dbName}")
        self.update()

    def add_db(self, dbName: str):
        dbOption = ft.dropdown.Option(dbName)
        self.dbDropdown.options.append(dbOption)
        self.update()