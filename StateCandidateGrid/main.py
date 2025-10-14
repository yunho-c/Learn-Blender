import bpy
import math
import os
from pathlib import Path

output_directory = str(Path(__file__).parent)


def setup_scene():
    """
    Cleans the default scene and sets up a new one with Suzanne, a camera, and a light.
    Returns the Suzanne object.
    """
    # Delete the default Cube if it exists
    if "Cube" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

    # Add Suzanne
    bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 0))
    suzanne = bpy.context.active_object
    suzanne.name = "Suzanne"

    # Smooth shading for a better look
    bpy.ops.object.shade_smooth()

    # Add a Subdivision Surface modifier for higher quality
    subdiv_modifier = suzanne.modifiers.new(name="Subdivision", type="SUBSURF")
    subdiv_modifier.levels = 2
    subdiv_modifier.render_levels = 2

    # Add and position a camera
    camera_data = bpy.data.cameras.new(name="RenderCamera")
    camera_object = bpy.data.objects.new("RenderCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    camera_object.location = (5, -5, 4)

    # Make the camera point at Suzanne using a constraint
    constraint = camera_object.constraints.new(type="TRACK_TO")
    constraint.target = suzanne
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"

    # Set this new camera as the active one for the scene
    bpy.context.scene.camera = camera_object

    # Add a light source
    light_data = bpy.data.lights.new(name="SunLight", type="SUN")
    light_data.energy = 2.5  # A nice bright sun
    light_object = bpy.data.objects.new(name="SunLight", object_data=light_data)
    bpy.context.scene.collection.objects.link(light_object)
    light_object.location = (4, -2, 6)
    light_object.rotation_euler[0] = math.radians(45)  # Angle it down

    return suzanne


def main():
    """
    Main function to run the rendering and saving process.
    """
    # Prepare the scene and get the object to rotate
    obj_to_rotate = setup_scene()

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Define the angles for the four orthogonal rotations
    angles_degrees = [0, 90, 180, 270]

    print("Starting render loop for Suzanne...")

    for i, angle in enumerate(angles_degrees):
        # Convert angle from degrees to radians
        rad = math.radians(angle)

        # Set the Z-axis rotation (up-axis)
        obj_to_rotate.rotation_euler[2] = rad

        # Define the output file path
        filepath = os.path.join(output_directory, f"suzanne_{i:02d}_{angle}deg.png")
        bpy.context.scene.render.filepath = filepath

        # Set render engine to Cycles for a better look (optional, EEVEE is faster)
        bpy.context.scene.render.engine = "CYCLES"
        bpy.context.scene.cycles.samples = 128

        # Make the background transparent
        bpy.context.scene.render.film_transparent = True

        # Render the image and save it
        bpy.ops.render.render(write_still=True)

        print(f"Saved render for {angle}° to {filepath}")

    # Optional: Reset rotation back to zero
    obj_to_rotate.rotation_euler[2] = 0

    # Save the .blend file
    blend_filepath = os.path.join(output_directory, "suzanne_scene.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_filepath)
    print(f"Saved .blend file to {blend_filepath}")

    print("Script finished successfully!")


# Standard Python entry point guard
if __name__ == "__main__":
    main()
