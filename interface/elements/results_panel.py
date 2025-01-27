import flet as ft
from interface.elements.ExpandableTiles import DynamicExpandableList
from interface.elements.PopupConfirmation import PopupConfirmation, ConfirmationResult
from logic import LogicManager
from page_manager import PageManager

class ResultsPanel(ft.Container):
    def __init__(self):
        super().__init__(expand=True)
        self._page_manager = PageManager()
        self._logic = LogicManager()
        self._list = DynamicExpandableList()
        self._init_controls()
        self._bind_controls()
        self.content = self._list

    def _init_controls(self):
        #Control buttons
        self._ebtn_sel_all = ft.ElevatedButton(
            text=" ",
            icon=ft.Icons.SELECT_ALL,
            tooltip="Select all results",
            expand=True
        )
        self._ebtn_des_all = ft.ElevatedButton(
            text=" ",
            icon=ft.Icons.CANCEL,
            tooltip="Deselect all results",
            expand=True
        )
        self._ebtn_move_to_processing = ft.ElevatedButton(
            text=" ",
            icon=ft.Icons.DOUBLE_ARROW,
            tooltip="Move selected results to the processing queue.",
            expand=True,
        )

        # Load results popup menu
        self._popupMnuItm_json = ft.PopupMenuItem(text="Load from a JSON backup file.")
        self._popupMnuItm_db = ft.PopupMenuItem(text="Load from DB", disabled=True, tooltip="Not yet implemented")
        self._popupMnuItm_clear_all = ft.PopupMenuItem(text="Clear all")
        self._popupMnuItm_clear_dupes = ft.PopupMenuItem(text="Clear Duplicates")
        self._popupMnuItm_clear_seen = ft.PopupMenuItem(text="Clear Seen")
        
        self._cnt_load_facade = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.UPLOAD_FILE_ROUNDED,
                        color="#A0CAFD",
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_DROP_DOWN,
                        color="#A0CAFD",
                        size=20,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=4,
            ),
            bgcolor="#191C20",
            padding=ft.padding.only(left=16, right=8, top=4, bottom=4),
            border_radius=20,
            ink=True,
        )
        self._cnt_clear_facade = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.DELETE,
                        color="#A0CAFD",
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_DROP_DOWN,
                        color="#A0CAFD",
                        size=20,
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=4,
            ),
            bgcolor="#191C20",
            padding=ft.padding.only(left=16, right=8, top=4, bottom=4),
            border_radius=20,
            ink=True,
        )
        self._popupMenubtn_load_file = ft.PopupMenuButton(
            content=self._cnt_load_facade,
            items=[self._popupMnuItm_json, self._popupMnuItm_db],
            expand=True,
            tooltip="Load from file or from DB."
        )
        self._popupMnuBtn_Clear = ft.PopupMenuButton(
            content=self._cnt_clear_facade,
            items=[self._popupMnuItm_clear_all, self._popupMnuItm_clear_dupes, self._popupMnuItm_clear_seen],
            expand=True,
            tooltip="Clear items from results."
        )
    
    def _confirm_action(self, e, action):
        confirmations = {
            "CLEAR_DUPES": ("Deleting Duplicates", "Are you sure you want to delete all duplicate entries?\nThis can waste API credits..."),
            "CLEAR_SEEN": ("Deleting Historical Results", "Are you sure you want to delete all previously seen results?"),
            "CLEAR_ALL": ("Deleting All Results", "Are you sure you want to delete all results?")
        }
        
        title, message = confirmations.get(action, ("Somethings happening...", "Are you ready to accept the consequences of your actions?"))
        
        popup = PopupConfirmation(
            title=title,
            message=message,
            on_result=self._handle_confirmation,
            context=action,
            page=self._page_manager.get_page()
        )
        self._page_manager.get_page().open(popup)
    
    def _handle_confirmation(self, result: ConfirmationResult, action: str):
        if result != ConfirmationResult.YES:
            return
            
        actions = {
            "CLEAR_DUPES": self._logic.clear_duplicates,
            "CLEAR_SEEN": self._logic.clear_seen,
            "CLEAR_ALL": self._logic.clear_results
        }
        
        if action_func := actions.get(action.upper()):
            mock_event = ft.ControlEvent(
                name="mock_confirmation",
                control=self,
                page=self._page_manager.get_page(),
                target=None,
                data=None
            )
            action_func(mock_event)
        else:
            print(f"Unknown action: {action}")

    def _bind_controls(self):
        self._popupMnuItm_db.on_click = lambda e: print("Load from DB")
        self._popupMnuItm_json.on_click = lambda e: self._logic.load_results_json(e)
        self._ebtn_sel_all.on_click = lambda e: self._logic.select_all_results(e)
        self._ebtn_des_all.on_click = lambda e: self._logic.deselect_all_results(e)
        self._popupMnuItm_clear_dupes.on_click = lambda e: self._confirm_action(e, "CLEAR_DUPES")
        self._popupMnuItm_clear_seen.on_click = lambda e: self._confirm_action(e, "CLEAR_SEEN")
        self._popupMnuItm_clear_all.on_click = lambda e: self._confirm_action(e, "CLEAR_ALL")
        self._ebtn_move_to_processing.on_click = lambda e: self._logic.move_to_processing(e)

    def get_controls(self):
        return [
            self._popupMenubtn_load_file,
            self._popupMnuBtn_Clear,
            self._ebtn_sel_all,
            self._ebtn_des_all,
            self._ebtn_move_to_processing
        ]

    def get_list(self):
        return self._list
    