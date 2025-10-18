import os
from pathlib import Path

import bpy


def get_texture_files(directory: Path) -> list:
    """Finds all image texture files in a given directory."""
    print(f"Searching for textures in: {directory}")
    if not directory.is_dir():
        print(f"Error: Directory not found at '{directory}'")
        return []

    supported_extensions = [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr"]

    found_files = []
    for item in directory.iterdir():
        if item.is_file() and item.suffix.lower() in supported_extensions:
            found_files.append(item.name)

    if not found_files:
        print(f"Warning: No supported image files found in '{directory}'.")
    else:
        print(f"Found {len(found_files)} texture files.")

    return found_files


def setup_principled_material(texture_dir: Path, texture_files: list):
    """
    Sets up a complete Blender scene and uses Node Wrangler to create a PBR material.
    """
    # Create an object to apply the material to (UV Sphere is good for viewing materials)
    bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0))
    # Add a subdivision surface for a smoother look
    bpy.ops.object.modifier_add(type="SUBSURF")
    bpy.context.object.modifiers["Subdivision"].levels = 2
    bpy.ops.object.shade_smooth()  # Make it smooth

    obj = bpy.context.active_object

    # Create a material and enable nodes
    mat = bpy.data.materials.new(name="Polyhaven_PBR_Material")
    obj.data.materials.append(mat)
    obj.active_material = mat  # Ensure the new material is the active one
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    principled_node = nodes.get("Principled BSDF")

    # Ensure the Principled BSDF is the active node for the operator
    principled_node.select = True
    nodes.active = principled_node

    # Operator Call with Context Override
    # This is the core logic. Node operators need a UI context to run.
    # We create a fake context by temporarily overriding it.

    window = bpy.context.window_manager.windows[0]
    screen = window.screen

    node_editor_area = None
    for area in screen.areas:
        if area.type == "NODE_EDITOR":
            node_editor_area = area
            break

    original_area_type = None
    if not node_editor_area:
        node_editor_area = screen.areas[0]
        original_area_type = node_editor_area.type
        node_editor_area.type = "NODE_EDITOR"

    node_space = node_editor_area.spaces.active

    node_space_has_ui_type = hasattr(node_space, "ui_type")
    original_ui_type = node_space.ui_type if node_space_has_ui_type else None

    node_space_has_tree_type = hasattr(node_space, "tree_type")
    original_tree_type = node_space.tree_type if node_space_has_tree_type else None

    node_space_has_shader_type = hasattr(node_space, "shader_type")
    original_shader_type = node_space.shader_type if node_space_has_shader_type else None

    node_space_has_node_tree = hasattr(node_space, "node_tree")
    original_node_tree = node_space.node_tree if node_space_has_node_tree else None

    if node_space_has_ui_type:
        node_space.ui_type = "ShaderNodeTree"
    elif node_space_has_tree_type:
        node_space.tree_type = "ShaderNodeTree"

    if node_space_has_shader_type:
        node_space.shader_type = "OBJECT"
    if node_space_has_node_tree:
        node_space.node_tree = mat.node_tree

    # Node Wrangler expects an absolute directory that mirrors the file browser output.
    directory_path = texture_dir.resolve()
    directory_str = str(directory_path)
    if not directory_str.endswith(os.sep):
        directory_str += os.sep

    # The `files` argument for the operator is a list of dicts containing file names.
    files_list = [{"name": Path(f).name} for f in texture_files]

    print("\nOverriding context to run Node Wrangler operator...")
    node_region = next(
        (region for region in node_editor_area.regions if region.type == "WINDOW"),
        node_editor_area.regions[0],
    )
    with bpy.context.temp_override(
        window=window,
        area=node_editor_area,
        region=node_region,
        space_data=node_space,
        edit_object=obj,
        active_object=obj,
    ):
        # This is the Node Wrangler operator doing all the heavy lifting
        bpy.ops.node.nw_add_textures_for_principled(directory=directory_str, files=files_list)

    if node_space_has_node_tree:
        node_space.node_tree = original_node_tree
    if node_space_has_shader_type:
        node_space.shader_type = original_shader_type
    if node_space_has_ui_type:
        node_space.ui_type = original_ui_type
    elif node_space_has_tree_type:
        node_space.tree_type = original_tree_type

    if original_area_type:
        node_editor_area.type = original_area_type

    print("Node Wrangler's Principled Setup operator executed successfully.")


if __name__ == "__main__":
    # # Scene Setup
    # # Start with a clean slate
    # bpy.ops.wm.read_factory_settings(use_empty=True)

    # Enable Node Wrangler Addon
    try:
        bpy.ops.preferences.addon_enable(module="node_wrangler")
        print("Node Wrangler addon enabled.")
    except Exception as e:
        print(
            f"Warning: Could not enable Node Wrangler. The script may fail. Error: {e}"
        )

    texture_directory = Path("./assets/aerial_rocks_02_1k.blend/textures")
    texture_filenames = get_texture_files(texture_directory)
    setup_principled_material(texture_directory, texture_filenames)

    # Save the Result
    output_path = Path("./polyhaven_output.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(output_path.resolve()))
    print(f"\nSaved final scene to: {output_path.resolve()}")
