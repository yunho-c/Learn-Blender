import bpy
import os

bpy.context.scene.render.engine = "CYCLES"
bpy.context.scene.cycles.samples = 256

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
    blur = tree.nodes.new("CompositorNodeBlur")
    sub = tree.nodes.new("CompositorNodeMixRGB")
    glare = tree.nodes.new("CompositorNodeGlare")
    mix = tree.nodes.new("CompositorNodeMixRGB")
    comp = tree.nodes.new("CompositorNodeComposite")

    # --- Configure nodes ---
    id_mask.index = pass_index

    blur.filter_type = "GAUSS"
    blur.size_x = 25  # Increase for thicker glow
    blur.size_y = 25
    blur.use_relative = False

    sub.blend_type = "SUBTRACT"
    sub.inputs[0].default_value = 1.0  # full strength

    glare.glare_type = "FOG_GLOW"
    glare.quality = "HIGH"
    glare.size = glare_size
    glare.mix = 0.0
    mix.blend_type = "ADD"

    # --- Link nodes ---
    links = tree.links
    links.new(rlayers.outputs["IndexOB"], id_mask.inputs["ID value"])
    links.new(id_mask.outputs["Alpha"], blur.inputs["Image"])  # Blur mask
    links.new(blur.outputs["Image"], sub.inputs[1])  # Blurred
    links.new(id_mask.outputs["Alpha"], sub.inputs[2])  # Original mask
    links.new(sub.outputs["Image"], glare.inputs["Image"])  # Edge -> Glare
    links.new(glare.outputs["Image"], mix.inputs[2])  # Glow -> Mix
    links.new(rlayers.outputs["Image"], mix.inputs[1])  # Base image
    links.new(mix.outputs["Image"], comp.inputs["Image"])


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
