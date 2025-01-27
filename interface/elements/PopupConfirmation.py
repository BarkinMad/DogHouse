import flet as ft
from typing import Callable, Any, Optional
from enum import Enum, auto

class ConfirmationResult(Enum):
    YES = auto()
    NO = auto()

class PopupConfirmation(ft.AlertDialog):
    def __init__(
        self, 
        title: str,
        message: str,
        on_result: Callable[[ConfirmationResult, Any], None],
        context: Any = None,
        yes_text: str = "Yes",
        no_text: str = "No",
        page: Optional[ft.Page] = None
    ):
        if not callable(on_result):
            raise ValueError("on_result must be callable")
            
        super().__init__(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton(yes_text, on_click=lambda e: self._handle_result(e, ConfirmationResult.YES)),
                ft.TextButton(no_text, on_click=lambda e: self._handle_result(e, ConfirmationResult.NO))
            ],
        )
        self._on_result = on_result
        self._context = context
        self._page = page

    def _handle_result(self, e: ft.ControlEvent, result: ConfirmationResult):
        try:
            print(self._on_result)
            self._on_result(result, self._context)
        except Exception as ex:
            print(f"Error in confirmation callback: {ex}")
        finally:
            if self._page:
                self._page.close(self)