import flet as ft
from interface.InterfaceBuilder import BuildUI
from console import DHConsole
from plugins.manager import PluginManager
from processor.manager import ProcessorManager
from data.db_manager import DBManager
from page_manager import PageManager
from logic import LogicManager

def main(page: ft.Page):
    # Singleton initializations
    PageManager(page=page)
    LogicManager()
    DBManager("./data/db.json")
    pluginManager = PluginManager()
    processorManager = ProcessorManager()
    console = DHConsole()

    BuildUI()

    console.print("Welcome to the Dog House. Your systems' worst fears start here.")
    console.print(f"Plugins loaded: d[<f=ffffff, b>, <{', '.join(pluginManager.get_all_plugins().keys())}>]")
    console.print(f"Processors loaded: d[<f=ffffff, b>, <{', '.join(processorManager.get_all_processors().keys())}>]")

ft.app(main)