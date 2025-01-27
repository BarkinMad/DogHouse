import flet as ft

class ResizableColumn(ft.Column):
    def __init__(
        self,
        controls=None,
        initial_width=200,
        min_width=100,
        max_width=800,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.controls = controls or []
        self.width = initial_width
        self.min_width = min_width
        self.max_width = max_width
        self._setup_container()

    def _setup_container(self):
        # Main content container
        self.content_container = ft.Container(
            content=ft.Column(controls=self.controls),
            width=self.width,
            bgcolor=ft.colors.WHITE,
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=ft.border_radius.all(4),
        )

        # Resize handle
        handle = ft.Container(
            width=8,
            height=40,
            bgcolor=ft.colors.GREY_400,
            border_radius=ft.border_radius.all(4),
        )

        # Create multiple drag targets for incremental resizing
        drag_targets = []
        for i in range(-50, 51, 10):  # Create targets from -50 to +50
            target = ft.DragTarget(
                content=ft.Container(
                    width=10,
                    height=None,
                    bgcolor=ft.colors.TRANSPARENT,
                ),
                data=str(i),  # Store the resize amount as string data
                on_accept=self._on_accept,
                group="resize"
            )
            drag_targets.append(target)

        # Stack drag targets horizontally
        target_row = ft.Row(
            controls=drag_targets,
            spacing=0,
        )

        # Wrap handle in draggable
        self.drag_handle = ft.Draggable(
            content=handle,
            content_feedback=ft.Container(
                width=8,
                height=40,
                bgcolor=ft.colors.GREY_400,
                opacity=0.5,
                border_radius=ft.border_radius.all(4),
            ),
            group="resize"
        )

        # Create row with content and handle
        row = ft.Row(
            [
                self.content_container,
                self.drag_handle,
                target_row,
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        super().__init__(controls=[row])

    def _on_accept(self, e):
        # Get the resize amount from the target's data
        resize_amount = int(e.data)
        
        # Calculate new width
        new_width = self.width + resize_amount
        
        # Constrain width
        new_width = max(self.min_width, min(self.max_width, new_width))
        
        # Update the width
        self.width = new_width
        self.content_container.width = new_width
        self.content_container.update()

def main(page: ft.Page):
    resizable_col = ResizableColumn(
        controls=[
            ft.Text("Resizable Column", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("Drag the handle on the right to resize"),
            ft.TextField(label="Example input"),
            ft.ElevatedButton("Click me"),
        ],
        initial_width=300,
    )
    
    page.add(resizable_col)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)