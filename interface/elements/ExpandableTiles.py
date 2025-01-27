
import flet as ft
from typing import Optional
from data.Models import AggResult
from webbrowser import open

class ExpandableListTile(ft.Container):
    def __init__(self, title: str, expanded_content: str, bgcolor=None):
        super().__init__()
        self.title = title
        self.expanded_content = expanded_content
        self.is_expanded = False
        self.isolated = True
        self.queue_index: Optional[int] = None
        self.parent_queue = None
        self.sync_selected = self._create_sync_selected()        
        self.bgcolor = bgcolor
    
        self.content_container = ft.Container(
            visible=False,
            height=0,
            content=ft.Text(
                self.expanded_content,
                size=14,
            ),
            padding=ft.padding.all(15),
        )
        
        self.checkbox = ft.Checkbox(
            value=False,
            on_change=self.sync_selected
        )

        self.web_open_button = ft.IconButton(
            icon=ft.Icons.OPEN_IN_BROWSER,
            on_click=self.open_url
        )

        self.list_tile = ft.ListTile(
            title=ft.Text(self.title),
            trailing=self.checkbox,
            on_click=self.toggle_expanded,
            bgcolor=bgcolor  
        )

        self.content = ft.Column(
            spacing=0,
            controls=[
                self.list_tile,
                self.content_container
            ]
        )

    def _create_sync_selected(self):
        def sync_selected(_):
            if self.parent_queue is not None and self.queue_index is not None:
                other = self.parent_queue.get_result_by_index(self.queue_index)
                if other:
                    setattr(other, "isSelected", self.checkbox.value)
        return sync_selected

    def toggle_expanded(self, _):
        self.is_expanded = not self.is_expanded
        self.content_container.visible = self.is_expanded
        self.content_container.height = None if self.is_expanded else 0
        self.update()

    def set_trailing(self, value = "CHECKBOX"):
        if value == "CHECKBOX":
            self.list_tile.trailing = self.checkbox
        elif value == "URL":
            self.list_tile.trailing = self.web_open_button

    @property
    def trailing(self):
        if isinstance(self.list_tile.trailing, ft.Checkbox):
            return "CHECKBOX"
        elif isinstance(self.list_tile.trailing, ft.IconButton):
            return "URL"

    def open_url(self, _):
        url = None
        if self.title.find(" "):
            url = self.title.split(" ")[0]
        else:
            url = self.title
        open(f"http://{url}")
        
class DynamicExpandableList(ft.Container):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.expand = True
        self.bgcolor = ft.Colors.PRIMARY_CONTAINER
        self.border_radius = 10
        self.padding = 10
        
        self.items: list[ExpandableListTile] = []
        self.items_column = ft.Column(
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        self.empty_state = ft.Container(
            content=ft.Text(
                "No items",
                color=ft.Colors.OUTLINE,
                text_align=ft.TextAlign.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
        
        self.content = ft.Container(
            content=self.empty_state,
            expand=True,
            height=350,
        )
        self._page = None

    def _safe_update(self):
        """Safely update the control only if it's properly attached to a page."""
        try:
            if hasattr(self, 'page') and self.page:
                self.update()
                if self.content.content == self.items_column:
                    self.items_column.update()
        except AssertionError:
            pass

    def _update_view(self):
        """Update the view content and attempt a safe update."""
        if self.items:
            self.items_column.controls = self.items
            self.content.content = self.items_column
        else:
            self.content.content = self.empty_state
        self._safe_update()

    def add_item(self, title: str, expanded_content: str, parent_queue=None, sync_index=None, selected=False, bgcolor=None, trailing="CHECKBOX"):
        expandable_tile = ExpandableListTile(title, expanded_content, bgcolor=bgcolor)
        expandable_tile.queue_index = sync_index
        expandable_tile.checkbox.value = selected
        expandable_tile.parent_queue = parent_queue
        expandable_tile.set_trailing(trailing)
        self.items.append(expandable_tile)
        self._update_view()

    def select_all(self):
        """Select all items in the list."""
        for item in self.items:
            item.checkbox.value = True
            if item.parent_queue is not None and item.queue_index is not None:
                item.sync_selected(None)
        self._safe_update()

    def clear_items(self):
        """Clear all items from the list."""
        self.items = []
        self._update_view()

    def did_mount(self):
        """Called when the control is added to the page."""
        super().did_mount()
        self._page = self.page
        self._update_view()

    def set_trailing_all(self, value="CHECKBOX"):
        """Set the trailing widget type for all items."""
        for item in self.items:
            item.set_trailing(value)
        self._safe_update()

    def get_selected_items(self):
        """Get all selected items in the list."""
        return [item for item in self.items if item.checkbox.value]

    def deselect_all(self):
        """Deselect all items in the list."""
        for item in self.items:
            item.checkbox.value = False
            if item.parent_queue is not None and item.queue_index is not None:
                item.sync_selected(None)
        self._safe_update()

    def get_item_count(self):
        """Get the total number of items in the list."""
        return len(self.items)