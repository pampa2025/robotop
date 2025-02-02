import bpy


def create_bounding_box_for_mesh():
    # Get all objects with _MESH suffix

    mesh_objects = [obj for obj in bpy.data.objects if obj.name.endswith('_MESH')]

    for mesh_obj in mesh_objects:
        # Get world matrix bounds
        world_matrix = mesh_obj.matrix_world
        bounds = [world_matrix @ vertex.co for vertex in mesh_obj.data.vertices]

        # Calculate bounds
        min_x = min(v.x for v in bounds)
        max_x = max(v.x for v in bounds)
        min_y = min(v.y for v in bounds)
        max_y = max(v.y for v in bounds)
        min_z = min(v.z for v in bounds)
        max_z = max(v.z for v in bounds)

        # Create bounding box cube
        bpy.ops.mesh.primitive_cube_add()
        bbox = bpy.context.active_object

        # Name the bounding box
        bbox.name = mesh_obj.name.replace('_MESH', '_bb')

        # Set dimensions and location based on bounds
        bbox.dimensions = (max_x - min_x, max_y - min_y, max_z - min_z)
        bbox.location = ((max_x + min_x)/2, (max_y + min_y)/2, (max_z + min_z)/2)

        # Make it wireframe
        bbox.display_type = 'WIRE'


# Run the function
create_bounding_box_for_mesh()
