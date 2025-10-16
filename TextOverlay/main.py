# NOTE: This script must be invoked from inside Blender GUI.
import bpy

# CONFIGURATION
# You can change these values to customize the labels

TEXT_SIZE = 0.4  # The font size of the text label
TEXT_OFFSET_Z = 0.5  # How far above the object's top the label should float
MATERIAL_NAME = "UI_Label_Material"  # The name for the special emissive material
EMISSION_COLOR = (1.0, 1.0, 1.0, 1.0)  # RGBA color (white by default)
EMISSION_STRENGTH = 7.0  # Brightness of the text. Increase for more glow.

# SCRIPT LOGIC


def create_or_get_emission_material(name, color, strength):
    """
    Checks if a material with the given name exists.
    If it exists, it returns it. If not, it creates a new emissive material.
    """
    # Check if the material already exists in the .blend file
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    # If not, create a new material
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    nodes.clear()

    # Create Emission and Material Output nodes
    node_emission = nodes.new(type="ShaderNodeEmission")
    node_emission.inputs["Color"].default_value = color
    node_emission.inputs["Strength"].default_value = strength
    node_emission.location = (0, 0)

    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    node_output.location = (250, 0)

    # Link Emission to Output
    links.new(node_emission.outputs["Emission"], node_output.inputs["Surface"])

    return mat


def create_ui_labels():
    """
    Main function to create and configure the text labels for selected objects.
    """
    # PRE-FLIGHT CHECKS
    # Check for an active camera
    if not bpy.context.scene.camera:
        print("ERROR: No active camera in the scene. Please add a camera.")
        return {"CANCELLED"}

    # Get only the selected mesh objects
    selected_objects = [
        obj for obj in bpy.context.selected_objects if obj.type == "MESH"
    ]

    if not selected_objects:
        print("INFO: No mesh objects selected. Please select objects to label.")
        return {"CANCELLED"}

    camera = bpy.context.scene.camera

    # Get or create the single material we'll use for all labels
    label_material = create_or_get_emission_material(
        MATERIAL_NAME, EMISSION_COLOR, EMISSION_STRENGTH
    )

    # MAIN LOOP
    # Process each selected object
    for target_obj in selected_objects:
        # Create a new text object at the world origin
        bpy.ops.object.text_add(location=(0, 0, 0))
        text_obj = bpy.context.active_object

        # CONFIGURE TEXT
        text_obj.name = f"{target_obj.name}_Label"
        text_obj.data.body = target_obj.name
        text_obj.data.size = TEXT_SIZE
        text_obj.data.align_x = "CENTER"
        text_obj.data.align_y = "CENTER"

        # SET UP HIERARCHY & POSITION
        text_obj.parent = target_obj
        # Position the text above the object's bounding box
        text_obj.location = (0, 0, target_obj.dimensions.z + TEXT_OFFSET_Z)

        # ASSIGN MATERIAL & VISIBILITY
        text_obj.data.materials.append(label_material)
        # # Disable shadows for a clean UI look
        # text_obj.shadow_mode = "NONE"

        # ADD CAMERA TRACKING CONSTRAINT
        constraint = text_obj.constraints.new(type="TRACK_TO")
        constraint.target = camera
        # FIX: Use TRACK_Z for text objects to make them face the camera correctly
        constraint.track_axis = "TRACK_Z"
        constraint.up_axis = "UP_Y"

    print(f"Successfully created UI labels for {len(selected_objects)} objects.")
    return {"FINISHED"}


# RUN THE SCRIPT
if __name__ == "__main__":
    create_ui_labels()
