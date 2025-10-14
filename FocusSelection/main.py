import bpy
import os

bpy.context.scene.render.engine = 'CYCLES'

def apply_glow_effect(object_name="Cube", pass_index=1, glare_size=9):
    scene = bpy.context.scene
    obj = bpy.data.objects.get(object_name)
    if not obj:
        print(f"Error: Object '{object_name}' not found.")
        return

    print(f"Setting up glow for object: '{obj.name}'")
    obj.pass_index = pass_index

    # --- Enable object index pass BEFORE node creation ---
    view_layer = bpy.context.view_layer
    view_layer.use_pass_object_index = True
    view_layer.update()

    # --- Enable compositor and reset nodes ---
    scene.use_nodes = True
    tree = scene.node_tree
    tree.nodes.clear()

    # --- Create compositor nodes ---
    rlayers = tree.nodes.new("CompositorNodeRLayers")
    id_mask = tree.nodes.new("CompositorNodeIDMask")
    glare = tree.nodes.new("CompositorNodeGlare")
    mix = tree.nodes.new("CompositorNodeMixRGB")
    comp = tree.nodes.new("CompositorNodeComposite")

    # --- Configure nodes ---
    id_mask.index = pass_index
    glare.glare_type = 'FOG_GLOW'
    glare.quality = 'HIGH'
    glare.size = glare_size
    glare.mix = 0.0
    mix.blend_type = 'ADD'

    # --- Position (optional) ---
    rlayers.location = (-500, 200)
    id_mask.location = (-300, 0)
    glare.location = (-100, 200)
    mix.location = (200, 100)
    comp.location = (400, 100)

    # --- Link nodes ---
    links = tree.links
    links.new(rlayers.outputs["Image"], mix.inputs[1])
    links.new(rlayers.outputs["IndexOB"], id_mask.inputs["ID value"])
    links.new(id_mask.outputs["Alpha"], glare.inputs["Image"])
    links.new(glare.outputs["Image"], mix.inputs[2])
    links.new(mix.outputs["Image"], comp.inputs["Image"])

    print("Compositor glow setup complete.")


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

    # Execute the render. The File Output node will handle saving.
    # We still set the main render output path, though it's not strictly needed for the final image.
    print(f"Rendering scene to: {OUTPUT_IMAGE_PATH}")
    bpy.ops.render.render(write_still=True)
    print("Render complete.")

    # Save the resulting .blend file
    print(f"Saving scene setup to: {SAVE_BLEND_PATH}")
    bpy.ops.wm.save_as_mainfile(filepath=SAVE_BLEND_PATH)


if __name__ == "__main__":
    main()
