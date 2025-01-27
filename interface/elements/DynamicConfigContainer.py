import flet as ft
from typing import Any, Dict, Type, Optional, List
from dataclasses import dataclass
from flet_dstring import DString, DStringConfig

@dataclass
class ConfigField:
    name: str
    type: Type
    default: Any
    description: str
    options: Optional[List[Any]] = None

class ConfigValueError(Exception):
    pass

class DynamicConfigContainer(ft.Container):
    def __init__(self):
        super().__init__()
        self.bgcolor = ft.Colors.ON_TERTIARY
        self.padding = 10
        self.height = 200
        self.expand = False
        self.border_radius = 5
        
        self.content_list = ft.ListView(
            expand=True,
            spacing=0,
            auto_scroll=True
        )
        
        self.empty_text = DString(
            "d[<f=9E9E9E, b>, <Select a processor>]"
        ).to_flet()
        self.empty_text.text_align = ft.TextAlign.CENTER
        
        self.content_list.controls.append(self.empty_text)
        self.content = self.content_list
        
        self._fields: Dict[str, ConfigField] = {}
        self._controls: Dict[str, ft.Control] = {}

    def convert_value(self, value: Any, target_type: Type) -> Any:
        try:
            if target_type == bool:
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ('true', '1', 'yes', 'on')
            if target_type == list:
                if isinstance(value, list):
                    return value
                return [item.strip() for item in str(value).split(',')]
            return target_type(value)
        except (ValueError, TypeError) as e:
            raise ConfigValueError(f"Cannot convert '{value}' to {target_type.__name__}: {str(e)}")

    def create_input_for_type(self, field: ConfigField) -> ft.Control:
        if field.type == bool:
            return ft.Checkbox(
                value=field.default,
                label=field.description,
            )
        elif field.type in (int, float):
            return ft.TextField(
                value=str(field.default),
                label=field.description,
                input_filter=ft.NumbersOnlyInputFilter(),
                keyboard_type=ft.KeyboardType.NUMBER
            )
        elif field.type == list:
            if field.options:
                options = [ft.dropdown.Option(str(opt)) for opt in field.options]
                return ft.Dropdown(
                    label=field.description,
                    options=options,
                    value=str(field.default)
                )
            return ft.TextField(
                value=','.join(map(str, field.default)) if isinstance(field.default, list) else str(field.default),
                label=field.description,
                hint_text="Comma-separated values"
            )
        else:
            return ft.TextField(
                value=str(field.default),
                label=field.description
            )

    def add_config_field(self, name: str, field_type: Type, default_value: Any, 
                        description: str, options: List[Any] = None):
        if len(self.content_list.controls) == 1 and self.content_list.controls[0] == self.empty_text:
            self.content_list.controls.clear()
            
        field = ConfigField(name, field_type, default_value, description, options)
        self._fields[name] = field
        
        control = self.create_input_for_type(field)
        self._controls[name] = control
        
        row = ft.Row(
            controls=[
                ft.Text(f"{name} ({field_type.__name__})", expand=1),
                control
            ],
            spacing=0
        )
        
        self.content_list.controls.append(row)
        self.update()

    def get_config_values(self) -> Dict[str, Any]:
        config = {}
        errors = []
        
        for name, control in self._controls.items():
            field = self._fields[name]
            try:
                raw_value = control.value
                config[name] = self.convert_value(raw_value, field.type)
            except ConfigValueError as e:
                errors.append(f"Error in {name}: {str(e)}")
        
        if errors:
            raise ConfigValueError("\n".join(errors))
        return config

    def set_config_values(self, values: Dict[str, Any]):
        for name, value in values.items():
            if name in self._controls:
                control = self._controls[name]
                if isinstance(control, ft.Checkbox):
                    control.value = bool(value)
                else:
                    control.value = str(value)
        self.update()

    def clear(self):
        self.content_list.controls.clear()
        self._fields.clear()
        self._controls.clear()
        self.content_list.controls.append(self.empty_text)
        self.update()