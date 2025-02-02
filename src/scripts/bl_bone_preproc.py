import bpy
import bmesh


def get_primary_bone_name(obj):
    """Determine the primary bone name based on vertex group weights"""
    if not obj.vertex_groups:
        return None

    # Calculate weight dominance per vertex group
    weight_sums = {vg.name: 0.0 for vg in obj.vertex_groups}
    vert_count = {vg.name: 0 for vg in obj.vertex_groups}

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')

    for vert in obj.data.vertices:
        for group in vert.groups:
            vg_name = obj.vertex_groups[group.group].name
            weight_sums[vg_name] += group.weight
            vert_count[vg_name] += 1

    # Find the most dominant vertex group
    max_avg = 0
    primary_bone = None
    for vg in obj.vertex_groups:
        avg = weight_sums[vg.name] / max(vert_count[vg.name], 1)
        if avg > max_avg:
            max_avg = avg
            primary_bone = vg.name

    return primary_bone


def process_mesh(obj):
    armature_mod = next((mod for mod in obj.modifiers if mod.type == 'ARMATURE' and mod.object), None)
    if not armature_mod:
        return

    armature = armature_mod.object
    original_name = obj.name
    bone_names = [b.name for b in armature.data.bones]

    # Apply transforms first
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Store original vertex groups
    original_groups = {vg.name: vg.index for vg in obj.vertex_groups}

    with bpy.context.temp_override(active_object=obj):
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        # Process each bone
        for bone_name in bone_names:
            if bone_name not in original_groups:
                continue

            # Select vertices for this bone
            bpy.ops.mesh.select_all(action='DESELECT')
            obj.vertex_groups.active_index = original_groups[bone_name]
            bpy.ops.object.vertex_group_select()

            # Check if any vertices selected
            if not any(v.select for v in bm.verts):
                continue

            # Duplicate and separate
            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.separate(type='SELECTED')

        bpy.ops.object.mode_set(mode='OBJECT')

    # Process separated parts
    separated_objects = [o for o in bpy.context.selected_objects if o != obj]
    for new_obj in separated_objects:
        # Clean vertex groups - keep only the primary bone
        primary_bone = get_primary_bone_name(new_obj)

        # Remove all non-primary vertex groups
        for vg in new_obj.vertex_groups[:]:
            if vg.name != primary_bone:
                new_obj.vertex_groups.remove(vg)

        # Rename based on primary bone
        if primary_bone:
            new_obj.name = f"{primary_bone}_MESH"

        # Setup armature modifier
        if 'Armature' not in new_obj.modifiers:
            mod = new_obj.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = armature

        # Parent to armature
        new_obj.parent = armature
        new_obj.matrix_parent_inverse = armature.matrix_world.inverted()

    # Hide original
    obj.hide_set(True)
    obj.hide_render = True


# Execute
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        process_mesh(obj)

print("Separation complete with proper bone naming!")
# export gltf settings:
{
    'apply_modifiers': True,
    'export_skins': True,
    'export_bake_skins': False,
    'export_yup': True,
    'export_selected': True,
    'export_animations': False
}
