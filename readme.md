Dog House 🐕

Dog House is an open-source GUI application built with Flet in Python, designed for cybersecurity professionals and enthusiasts. It provides a modular and extensible platform for aggregating and processing IP data from various cybersecurity services like Shodan, Zoomeye, and more. With its plugin-based architecture, Dog House allows users to create custom integrations and batch processing workflows tailored to their specific needs.
Features

    Modular Aggregator Plugins: Easily integrate with "banned aggregators" or any cybersecurity service by creating custom plugins. Plugins can define their own UI controls, configuration fields, and search logic.

    Custom Processors: Build and run batch processing operations on IP results using customizable processor plugins. Processors can handle tasks like filtering, enrichment, or exporting data.

    Console Interface: Interact with the application via a built-in console for real-time feedback and control.

    Search History & Deduplication: Automatically saves search history in a database to filter out duplicate results.

    Extensible & Customizable: Designed to be highly modular, allowing users to extend functionality with their own plugins and processors.

    User-Friendly GUI: Built with Flet, providing an intuitive and responsive graphical interface.

Installation

    Clone the Repository:
    bash
    Copy

    git clone https://github.com/yourusername/dog-house.git
    cd dog-house

    Install Dependencies:
    bash
    Copy

    pip install -r requirements.txt

    Run the Application:
    bash
    Copy

    flet main.py

Usage
Aggregator Plugins

    Create custom aggregator plugins to fetch data from services like Shodan, Zoomeye, or any other API.

    Plugins can define their own UI controls (e.g., text fields, buttons, dropdowns) and configuration fields.

    Place your plugin in the plugins/custom/ directory.

    Example plugin structure:
    python
    Copy

    from plugins.base import PluginBase, SearchResult, FletControlConfig, FletControlType

    class MyAggregator(PluginBase):
        @property
        def name(self) -> str:
            return "My Aggregator"

        @property
        def description(self) -> str:
            return "Fetches data from My Service"

        def get_ui_controls(self) -> List[FletControlConfig]:
            return [
                FletControlConfig(
                    control_type=FletControlType.TEXTFIELD,
                    id="query",
                    label="Search Query",
                    required=True
                )
            ]

        async def search(self, query: str, config: Dict[str, Any] = None) -> List[SearchResult]:
            # Your logic to fetch data from the service
            return results

Processor Plugins

    Create custom processor plugins to handle and process IP results.

    Processors can define their own configuration properties and processing logic.

    Place your plugin in the processors/custom/ directory.

    Example plugin structure:
    python
    Copy

    from processors.base import ProcessorBase, ProcessingResult, ConfigProperty

    class MyProcessor(ProcessorBase):
        @property
        def name(self) -> str:
            return "My Processor"

        @property
        def description(self) -> str:
            return "Processes IP data for My Task"

        @property
        def config_properties(self) -> list[ConfigProperty]:
            return [
                ConfigProperty(
                    name="threshold",
                    type=int,
                    default=10,
                    description="Threshold value for processing"
                )
            ]

        async def process(self, target: dict) -> ProcessingResult:
            # Your logic to process IP data
            return ProcessingResult(success=True, message="Processing complete")

Plugin Development
Aggregator Plugin Template
python
Copy

from plugins.base import PluginBase, SearchResult, FletControlConfig, FletControlType

class MyAggregator(PluginBase):
    @property
    def name(self) -> str:
        return "My Aggregator"

    @property
    def description(self) -> str:
        return "Fetches data from My Service"

    def get_ui_controls(self) -> List[FletControlConfig]:
        return [
            FletControlConfig(
                control_type=FletControlType.TEXTFIELD,
                id="query",
                label="Search Query",
                required=True
            )
        ]

    async def search(self, query: str, config: Dict[str, Any] = None) -> List[SearchResult]:
        # Implement your data fetching logic here
        return results

Processor Plugin Template
python
Copy

from processors.base import ProcessorBase, ProcessingResult, ConfigProperty

class MyProcessor(ProcessorBase):
    @property
    def name(self) -> str:
        return "My Processor"

    @property
    def description(self) -> str:
        return "Processes IP data for My Task"

    @property
    def config_properties(self) -> list[ConfigProperty]:
        return [
            ConfigProperty(
                name="threshold",
                type=int,
                default=10,
                description="Threshold value for processing"
            )
        ]

    async def process(self, target: dict) -> ProcessingResult:
        # Implement your data processing logic here
        return ProcessingResult(success=True, message="Processing complete")

Contributing

We welcome contributions! If you'd like to contribute to Dog House, please follow these steps:

    Fork the repository.

    Create a new branch for your feature or bugfix.

    Submit a pull request with a detailed description of your changes.

License

Dog House is released under the MIT License. See the LICENSE file for more details.
Support

If you encounter any issues or have questions, feel free to open an issue on the GitHub repository.
Acknowledgments

    Flet: For providing the framework to build the GUI.

    Shodan, Zoomeye, and other aggregators: For their invaluable cybersecurity data services.

🐶 Happy Hacking! 🐶