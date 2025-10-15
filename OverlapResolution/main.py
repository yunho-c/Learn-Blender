# This script demonstrates how Blender's physics engine resolves an initial overlap
# between two rigid body objects. It creates a static plane and an active cube
# that intersects the plane.
#
# This version is designed for STANDALONE INVOCATION (e.g., `blender --background --python <script_name>.py`).
# It will automatically bake the physics, render an animation, and save the .blend file.

import bpy
import os

# --- Scene Setup ---
# Clear existing mesh objects from the scene to start fresh.
# This makes the script reusable without manual cleanup.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.select_by_type(type="MESH")
bpy.ops.object.delete()

# --- Create the Plane (Passive Rigid Body) ---
# Add a plane to serve as the ground or collision surface.
bpy.ops.mesh.primitive_plane_add(
    size=10, enter_editmode=False, align="WORLD", location=(0, 0, 0)
)
plane = bpy.context.object
plane.name = "GroundPlane"

# Add Rigid Body physics to the plane.
bpy.ops.rigidbody.object_add()
# Set the type to 'PASSIVE'. Passive objects are static colliders; they
# affect other rigid bodies but are not affected by them or by gravity.
plane.rigid_body.type = "PASSIVE"
plane.rigid_body.collision_shape = "BOX"  # 'BOX' is efficient for a flat plane

print("Created a passive ground plane.")

# --- Create the Cube (Active Rigid Body) ---
# Add a cube to the scene. We will place it so it overlaps the plane.
# The default cube is 2x2x2 units, so a Z location of 0.5 places its
# origin above the plane, but its bottom half below it.
bpy.ops.mesh.primitive_cube_add(
    size=2, enter_editmode=False, align="WORLD", location=(0, 0, 0.5)
)
cube = bpy.context.object
cube.name = "BouncingCube"

# Add Rigid Body physics to the cube.
bpy.ops.rigidbody.object_add()
# The default type is 'ACTIVE', which is what we want. Active objects
# are fully dynamic and are affected by forces, gravity, and collisions.
cube.rigid_body.type = "ACTIVE"
cube.rigid_body.collision_shape = "BOX"

# --- Tweak Physics Properties to Reduce Bouncing ---
# Increase damping to make the cube lose energy faster, preventing a large bounce.
# A higher value absorbs the "pop" from the overlap correction.
cube.rigid_body.linear_damping = 1.0
cube.rigid_body.angular_damping = 1.0


print("Created an active cube overlapping the plane.")
print("Increased damping to reduce overshoot.")

# --- Animation & Timeline Setup ---
# Set the timeline to the first frame so the simulation starts from the beginning.
bpy.context.scene.frame_set(1)
bpy.context.scene.frame_end = 60  # We'll render a 60-frame animation

# Ensure the rigid body world is present (usually is by default)
if not bpy.context.scene.rigidbody_world:
    bpy.ops.rigidbody.world_add()

# Increase the solver iterations for a more accurate and stable simulation.
# This helps the solver find a better solution for the initial overlap
# without applying an excessive corrective force.
bpy.context.scene.rigidbody_world.solver_iterations = 30
print("Increased rigid body solver iterations for stability.")

# --- Bake Physics ---
# Baking is essential for rendering animations with physics in standalone mode.
# It pre-calculates the simulation and stores it.
print("Baking physics simulation...")
bpy.ops.ptcache.bake_all(bake=True)
print("Baking complete.")

# --- Rendering Setup ---
# Define a base directory for output files.
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(script_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# Configure render settings for a quick video output.
render_path = os.path.join(output_dir, "physics_bounce.mp4")
bpy.context.scene.render.filepath = render_path
bpy.context.scene.render.image_settings.file_format = "FFMPEG"
bpy.context.scene.render.ffmpeg.format = "MPEG4"
bpy.context.scene.render.ffmpeg.codec = "H264"
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"  # Use Eevee for speed

# --- Render the Animation ---
print(f"Rendering animation to {render_path}...")
bpy.ops.render.render(animation=True)
print("Rendering finished.")

# --- Save the Blend File ---
# Save the final .blend file in the same output directory.
save_path = os.path.join(output_dir, "physics_overlap_demo.blend")
bpy.ops.wm.save_as_mainfile(filepath=save_path)

print("\n--- Script Finished ---")
print(f"Scene saved to: {save_path}")
print(f"Animation rendered to: {render_path}")
