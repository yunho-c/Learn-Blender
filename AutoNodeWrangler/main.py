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

    if not node_editor_area:
        node_editor_area = screen.areas[0]
        node_editor_area.type = "NODE_EDITOR"

    # The `files` argument for the operator is a list of dicts
    files_list = [{"name": f} for f in texture_files]

    print("\nOverriding context to run Node Wrangler operator...")
    with bpy.context.temp_override(
        window=window, area=node_editor_area, region=node_editor_area.regions[0]
    ):
        # This is the Node Wrangler operator doing all the heavy lifting
        bpy.ops.node.nw_add_textures_for_principled(directory=str(texture_dir), files=files_list)

    if node_editor_area.type != "PROPERTIES":  # Revert to a safe default
        node_editor_area.type = "PROPERTIES"

    print("Node Wrangler's Principled Setup operator executed successfully.")


if __name__ == "__main__":
    # # Scene Setup
    # # Start with a clean slate
    # bpy.ops.wm.read_factory_settings(use_empty=True)

    # Enable Node Wrangler Addon
    try:
        bpy.ops.preferences.addon_enable(module="node_wrangler")
        print("Node Wrangler addon enabled.")
        print(list(dir(bpy.ops.node)))
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
