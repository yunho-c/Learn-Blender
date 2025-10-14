import math
import os
from pathlib import Path

import bpy
import numpy as np
from PIL import Image

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


def render(output_path=None):
    """
    Renders the current scene, either saving to a file or returning as a NumPy array.

    Args:
        output_path (str, optional): If provided, the path to save the rendered image.
                                     If None, the function returns a NumPy array.
                                     Defaults to None.

    Returns:
        np.ndarray or None: If output_path is None, returns a NumPy array of the
                            rendered image. Otherwise, returns None.
    """
    if output_path:
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)
        return None
    else:
        bpy.ops.render.render(write_still=False)
        render_result = bpy.data.images.get("Render Result")
        if not render_result:
            raise RuntimeError("Render result not found. The render may have failed.")

        width = render_result.width
        height = render_result.height
        pixels = np.array(render_result.pixels[:])

        image = pixels.reshape((height, width, 4))
        image = np.flipud(image)
        return image


def create_collage(image_paths, output_path):
    """
    Creates a 2x2 collage from a list of 4 images using Pillow.

    Args:
        image_paths (list of str): A list of 4 paths to the input images.
        output_path (str): The path to save the collage image.
    """
    if Image is None:
        print("\nCollage creation skipped: Pillow library not found.")
        print("Please install it to enable this feature: pip install Pillow")
        return

    if len(image_paths) != 4:
        raise ValueError("This function requires exactly 4 images for a 2x2 collage.")

    images = [Image.open(p) for p in image_paths]

    # Assuming all images are the same size
    width, height = images[0].size
    collage_width = 2 * width
    collage_height = 2 * height
    collage_image = Image.new("RGBA", (collage_width, collage_height))

    # Paste images into the collage
    collage_image.paste(images[0], (0, 0))
    collage_image.paste(images[1], (width, 0))
    collage_image.paste(images[2], (0, height))
    collage_image.paste(images[3], (width, height))

    collage_image.save(output_path)
    print(f"\nCollage saved to {output_path}")


def main():
    """
    Main function to run the rendering and saving process.
    """
    # Prepare the scene and get the object to rotate
    obj_to_rotate = setup_scene()

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Set render settings
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.render.film_transparent = True

    # Define the angles for the four orthogonal rotations
    angles_degrees = [0, 90, 180, 270]
    image_filepaths = []

    print("Starting render loop for Suzanne...")

    for i, angle in enumerate(angles_degrees):
        # Convert angle from degrees to radians
        rad = math.radians(angle)

        # Set the Z-axis rotation (up-axis)
        obj_to_rotate.rotation_euler[2] = rad

        # Define the output file path and render to file
        filepath = os.path.join(output_directory, f"suzanne_{i:02d}_{angle}deg.png")
        render(output_path=filepath)
        image_filepaths.append(filepath)

        print(f"Saved render for {angle}° to {filepath}")

    collage_output_path = os.path.join(output_directory, "suzanne_collage.png")
    create_collage(image_filepaths, collage_output_path)

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
