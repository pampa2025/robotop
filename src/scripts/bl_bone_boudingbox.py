import bpy

# Get all bounding boxes and their corresponding target mesh objects
bounding_boxes = [obj for obj in bpy.context.scene.objects if obj.name.startswith("BoundingBox_")]
target_meshes = [obj for obj in bpy.context.scene.objects if obj.name.startswith("TargetMesh_")]

# Ensure the number of bounding boxes matches the number of target meshes
if len(bounding_boxes) != len(target_meshes):
    raise ValueError("The number of bounding boxes does not match the number of target meshes.")

# Iterate over each bounding box and its corresponding target mesh
for bbox, target_mesh in zip(bounding_boxes, target_meshes):
    # Get the position and rotation of the target mesh
    target_position = target_mesh.location
    target_rotation = target_mesh.rotation_euler

    # Apply the position and rotation to the bounding box
    bbox.location = target_position
    bbox.rotation_euler = target_rotation
