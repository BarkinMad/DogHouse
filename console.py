#/console.py
import flet as ft
import datetime
import flet
from flet_dstring import DString, DStringConfig

class DHConsole:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.messages = []
            cls._instance.container = ft.Container(bgcolor=ft.Colors.BLACK, padding=5, height=200, border_radius=5)
            cls._instance.listView = ft.ListView(auto_scroll=True, spacing=0)
            cls._instance.selection = ft.SelectionArea(content=cls._instance.listView)
            cls._instance.container.content = cls._instance.selection
        return cls._instance

    def print(self, message, severity="info"):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._instance.messages.append({
            "message": message,
            "severity": severity,
            "date": date
        })

        icon = None
        if severity == "info":
            icon = ft.Icons.INFO
        elif severity == "warning":
            icon = ft.Icons.WARNING
        elif severity == "error":
            icon = ft.Icons.ERROR

        dateFormatStr = f"d[<f=ffffff,w=bold,size=12>, <{date.split(" ")[1]}>] "
        leading = "d[<f=ff6b6b,w=bold,size=14>, <DH$>>] "
        text = f"{dateFormatStr}{leading} {message}"
        dtext: ft.Text = DString(text, DStringConfig(default_color=ft.Colors.AMBER, default_size=12)).to_flet()

        self._instance.listView.controls.append(dtext)
        try:
            self._instance.container.update()
        except Exception as ex:
            pass

    def clear(self):
        self._instance.messages = []
        self.update()

    def get_console(self):
        return self._instance.container