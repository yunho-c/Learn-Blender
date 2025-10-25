import random
from typing import Dict, Iterable, Optional, Sequence, Tuple

import bpy


def _iter_interface_items(items: Iterable) -> Iterable:
    """Yield every item (including nested panel items) from a Geometry Nodes interface."""
    for item in items:
        yield item
        children = getattr(item, "items_tree", None)
        if children:
            yield from _iter_interface_items(children)


class DoorItInteriorController:
    """Convenience wrapper for adjusting Door It! Interior Geometry Nodes parameters."""

    def __init__(self, obj: Optional[bpy.types.Object] = None, modifier_name: str = "GeometryNodes"):
        self.object = obj or bpy.context.object
        if self.object is None:
            raise ValueError("No active object found. Pass an object explicitly or select one in the viewport.")
        self.modifier = self._resolve_modifier(modifier_name)
        self._socket_cache: Dict[str, bpy.types.Property] = {}

    def _resolve_modifier(self, preferred_name: str) -> bpy.types.NodesModifier:
        if preferred_name in self.object.modifiers:
            mod = self.object.modifiers[preferred_name]
            if mod.type == 'NODES':
                return mod
        for mod in self.object.modifiers:
            if mod.type == 'NODES':
                return mod
        raise ValueError(f"No Geometry Nodes modifier found on object '{self.object.name}'.")

    def _get_interface_item(self, label: str):
        if label in self._socket_cache:
            return self._socket_cache[label]

        interface = self.modifier.node_group.interface
        for item in _iter_interface_items(interface.items_tree):
            if getattr(item, "name", None) == label and hasattr(item, "identifier"):
                self._socket_cache[label] = item
                return item

        raise KeyError(f"Socket labeled '{label}' not found on modifier '{self.modifier.name}'.")

    def _set_numeric(self, label: str, value: float) -> float:
        item = self._get_interface_item(label)
        min_value = getattr(item, "min_value", None)
        max_value = getattr(item, "max_value", None)

        numeric_value = float(value)
        if min_value is not None:
            numeric_value = max(numeric_value, float(min_value))
        if max_value is not None:
            numeric_value = min(numeric_value, float(max_value))

        self.modifier[item.identifier] = numeric_value
        return numeric_value

    def set_width(self, value: float) -> float:
        """Set the door width socket in meters. Returns the applied value (clamped if needed)."""
        return self._set_numeric("Width", value)

    def set_height(self, value: float) -> float:
        """Set the door height socket in meters. Returns the applied value (clamped if needed)."""
        return self._set_numeric("Height", value)

    def set_type(self, value: int) -> int:
        """Set the style/type index. Returns the applied integer value."""
        item = self._get_interface_item("Type")
        int_value = int(value)
        min_value = int(getattr(item, "min_value", int_value))
        max_value = int(getattr(item, "max_value", int_value))
        clamped_value = max(min_value, min(int_value, max_value))
        self.modifier[item.identifier] = clamped_value
        return clamped_value

    def randomize_type(self) -> int:
        """Pick a random valid style index and apply it."""
        item = self._get_interface_item("Type")
        min_value = int(getattr(item, "min_value", 0))
        max_value = int(getattr(item, "max_value", min_value))
        choice = random.randint(min_value, max_value)
        self.modifier[item.identifier] = choice
        return choice

    def set_paint_color(self, color: Sequence[float]) -> Tuple[float, float, float, float]:
        """Set the RGBA paint color. Returns the applied color tuple."""
        item = self._get_interface_item("Paint Color")
        if len(color) not in (3, 4):
            raise ValueError("Paint color must have 3 (RGB) or 4 (RGBA) components.")

        rgba = tuple(float(c) for c in color[:4])
        if len(rgba) == 3:
            rgba = (*rgba, 1.0)

        self.modifier[item.identifier] = rgba
        return rgba

    def randomize_paint_color(self, alpha: float = 1.0) -> Tuple[float, float, float, float]:
        """Assign a random RGB color with the given alpha."""
        rgba = (random.random(), random.random(), random.random(), float(alpha))
        self.set_paint_color(rgba)
        return rgba


def apply_door_settings(
    width: Optional[float] = None,
    height: Optional[float] = None,
    door_type: Optional[int] = None,
    randomize_type: bool = False,
    paint_color: Optional[Sequence[float]] = None,
    randomize_color: bool = False,
    alpha: float = 1.0,
    obj: Optional[bpy.types.Object] = None,
    modifier_name: str = "GeometryNodes",
    trigger_rebuild: bool = True,
) -> Dict[str, object]:
    """Apply a batch of settings to the Door It! Interior Geometry Nodes modifier.

    Returns a dictionary summarizing the values that were applied. If ``trigger_rebuild`` is
    ``True`` the object's dependency graph is updated so the viewport reflects the changes.
    """
    controller = DoorItInteriorController(obj=obj, modifier_name=modifier_name)
    results: Dict[str, object] = {"object": controller.object.name}

    if width is not None:
        results["width"] = controller.set_width(width)
    if height is not None:
        results["height"] = controller.set_height(height)

    if door_type is not None:
        results["type"] = controller.set_type(door_type)
    elif randomize_type:
        results["type"] = controller.randomize_type()

    if paint_color is not None:
        results["paint_color"] = controller.set_paint_color(paint_color)
    elif randomize_color:
        results["paint_color"] = controller.randomize_paint_color(alpha=alpha)

    if trigger_rebuild:
        controller.object.update_tag()
        view_layer = bpy.context.view_layer
        if view_layer is not None:
            view_layer.update()

    return results


if __name__ == "__main__":
    # Example usage: tweak values here and run the script from Blender's text editor.
    SETTINGS = {
        "width": 0.9144,          # 36 inches in meters
        "height": 2.032,          # 80 inches in meters
        "door_type": None,        # Set to an int to force a style, or keep None to randomize
        "randomize_type": True,   # Ignored when 'door_type' is provided
        "paint_color": None,      # Provide (R, G, B[, A]) or leave None to randomize
        "randomize_color": True,  # Ignored when 'paint_color' is provided
        "alpha": 1.0,             # Alpha channel for randomized colors
        "obj": None,              # Target object; None uses the active object
        "modifier_name": "GeometryNodes",
        "trigger_rebuild": True,  # Forces a depsgraph update after applying settings
    }

    applied = apply_door_settings(**SETTINGS)
    print("Applied Door It! Interior settings:", applied)
