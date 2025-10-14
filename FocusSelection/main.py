import bpy
import os

def apply_glow_effect(object_name="Cube", pass_index=1, glare_size=9):
    """
    This is the same core logic from apply_glow_headless.py,
    now running directly within this script's environment.
    """
    try:
        scene = bpy.context.scene # Context is now directly available
        obj = bpy.data.objects[object_name]
    except (KeyError, IndexError):
        print(f"Error: Object '{object_name}' not found.")
        return

    print(f"Setting up glow for object: '{obj.name}'")
    obj.pass_index = pass_index
    bpy.context.view_layer.use_pass_object_index = True

    # --- Build Compositor Node Tree (identical logic) ---
    scene.use_nodes = True
    tree = scene.node_tree
    for node in tree.nodes:
        tree.nodes.remove(node)
    # ... (node creation and linking logic remains the same) ...
    print("Compositor setup complete.")

def main():
    # --- Configuration ---
    TARGET_OBJECT = "Cube"
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    OUTPUT_IMAGE_PATH = os.path.join(OUTPUT_DIR, "glow_cube_direct.png")
    SAVE_BLEND_PATH = os.path.join(OUTPUT_DIR, "glow_setup_direct.blend")

    # --- Main Execution ---
    # NOTE: You might need to load a file first if not using the default scene
    # bpy.ops.wm.open_mainfile(filepath="path/to/your/file.blend")

    # Call the setup function directly
    apply_glow_effect(TARGET_OBJECT)

    # Configure and execute the render
    bpy.context.scene.render.filepath = OUTPUT_IMAGE_PATH
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    print(f"Rendering scene to: {OUTPUT_IMAGE_PATH}")
    bpy.ops.render.render(write_still=True)
    print("Render complete.")

    # Save the resulting .blend file
    print(f"Saving scene setup to: {SAVE_BLEND_PATH}")
    bpy.ops.wm.save_as_mainfile(filepath=SAVE_BLEND_PATH)


if __name__ == "__main__":
    main()
