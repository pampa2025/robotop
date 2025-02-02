import bpy
import bmesh

def process_mesh(obj):
    # Get armature modifier
    armature_mod = next((mod for mod in obj.modifiers if mod.type == 'ARMATURE' and mod.object), None)
    if not armature_mod:
        print(f"No valid armature modifier found on {obj.name}")
        return

    armature = armature_mod.object
    bone_names = [bone.name for bone in armature.data.bones]
    processed_groups = set()

    # Make object active and enter edit mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Create bmesh for selection checks
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()

    # Process each vertex group
    for vg in obj.vertex_groups:
        if vg.name not in bone_names:
            continue

        # Deselect all vertices
        bpy.ops.mesh.select_all(action='DESELECT')
        obj.vertex_groups.active = vg
        
        # Select vertices in this group
        bpy.ops.object.vertex_group_select()
        
        # Check if any vertices are selected
        selected_verts = [v for v in bm.verts if v.select]
        if not selected_verts:
            continue

        # Separate selected vertices
        bpy.ops.mesh.separate(type='SELECTED')
        
        # Exit to object mode to rename new object
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Find and rename new object
        new_objects = [o for o in bpy.context.selected_objects if o != obj]
        for new_obj in new_objects:
            new_obj.name = f"{vg.name}_MESH"
            # Keep armature modifier
            new_mod = new_obj.modifiers.new(name="Armature", type='ARMATURE')
            new_mod.object = armature
        
        # Re-enter edit mode for further processing
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)  # Refresh bmesh after separation

    # Cleanup
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Delete original mesh if empty
    if len(obj.data.vertices) == 0:
        bpy.data.objects.remove(obj, do_unlink=True)
    else:
        print(f"Original mesh {obj.name} has remaining vertices, not deleted")

# Process all selected mesh objects
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        process_mesh(obj)

print("Separation complete! Check your outliner for new mesh parts.")