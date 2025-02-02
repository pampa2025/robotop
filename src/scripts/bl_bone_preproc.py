import bpy
import bmesh


def process_mesh(obj):
    # Apply transforms on original mesh
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    armature_mod = next((mod for mod in obj.modifiers if mod.type == 'ARMATURE' and mod.object), None)
    if not armature_mod:
        print(f"No armature found on {obj.name}")
        return

    armature = armature_mod.object
    bone_names = [bone.name for bone in armature.data.bones]

    # Store original vertex groups
    original_groups = {vg.name: vg.index for vg in obj.vertex_groups}

    with bpy.context.temp_override(active_object=obj):
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        for bone_name in bone_names:
            if bone_name not in original_groups:
                continue

            # Select vertices belonging to this bone
            bpy.ops.mesh.select_all(action='DESELECT')
            obj.vertex_groups.active_index = original_groups[bone_name]
            bpy.ops.object.vertex_group_select()

            # Check if any vertices selected
            if not any(v.select for v in bm.verts):
                continue

            # Duplicate selection
            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.separate(type='SELECTED')

        bpy.ops.object.mode_set(mode='OBJECT')

    # Process separated parts
    separated_objects = [o for o in bpy.context.selected_objects if o != obj]
    for new_obj in separated_objects:
        # Cleanup vertex groups
        groups_to_keep = []
        for vg in new_obj.vertex_groups:
            if vg.name in bone_names:
                groups_to_keep.append(vg.name)

        # Remove non-bone vertex groups
        for vg in new_obj.vertex_groups:
            if vg.name not in groups_to_keep:
                new_obj.vertex_groups.remove(vg)

        # Apply transforms and setup modifiers
        bpy.context.view_layer.objects.active = new_obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Add armature modifier
        if not any(m for m in new_obj.modifiers if m.type == 'ARMATURE'):
            mod = new_obj.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = armature

        # Parent to armature with correct transform
        new_obj.parent = armature
        new_obj.matrix_parent_inverse = armature.matrix_world.inverted()

    # Hide original mesh
    obj.hide_set(True)
    obj.hide_render = True


# Process selected objects
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        process_mesh(obj)

print("Processing complete! Bone hierarchy and transforms are now preserved.")


# export gltf settings:
{
    'apply_modifiers': True,
    'export_skins': True,
    'export_bake_skins': False,
    'export_yup': True,
    'export_selected': True,
    'export_animations': False
}
