import bpy
import bmesh
import mathutils


def get_primary_bone_name(obj):
    """Determine the primary bone name based on vertex group weights"""
    if not obj.vertex_groups:
        return None

    weight_sums = {vg.name: 0.0 for vg in obj.vertex_groups}
    vert_count = {vg.name: 0 for vg in obj.vertex_groups}

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')

    for vert in obj.data.vertices:
        for group in vert.groups:
            vg_name = obj.vertex_groups[group.group].name
            weight_sums[vg_name] += group.weight
            vert_count[vg_name] += 1

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
    bone_names = [b.name for b in armature.data.bones]

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    original_groups = {vg.name: vg.index for vg in obj.vertex_groups}

    with bpy.context.temp_override(active_object=obj):
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        for bone_name in bone_names:
            if bone_name not in original_groups:
                continue

            bpy.ops.mesh.select_all(action='DESELECT')
            obj.vertex_groups.active_index = original_groups[bone_name]
            bpy.ops.object.vertex_group_select()

            if not any(v.select for v in bm.verts):
                continue

            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.separate(type='SELECTED')

        bpy.ops.object.mode_set(mode='OBJECT')

    separated_objects = [o for o in bpy.context.selected_objects if o != obj]
    for new_obj in separated_objects:
        primary_bone = get_primary_bone_name(new_obj)

        for vg in new_obj.vertex_groups[:]:
            if vg.name != primary_bone:
                new_obj.vertex_groups.remove(vg)

        if primary_bone:
            new_obj.name = f"{primary_bone}_MESH"

        if 'Armature' not in new_obj.modifiers:
            mod = new_obj.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = armature

        # Calculate bounding box dimensions and center
        bbox_corners = [new_obj.matrix_world @ mathutils.Vector(corner)
                        for corner in new_obj.bound_box]
        bbox_center = sum(bbox_corners, mathutils.Vector()) / 8
        bbox_dimensions = new_obj.dimensions

        # Create bounding box object
        bbox_mesh = bpy.data.meshes.new(f"{primary_bone}_BBOX")
        bbox_obj = bpy.data.objects.new(f"{primary_bone}_BBOX", bbox_mesh)
        bpy.context.collection.objects.link(bbox_obj)

        # Create cube mesh for bbox
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1)
        bm.to_mesh(bbox_mesh)
        bm.free()

        # Position and scale bbox
        bbox_obj.location = bbox_center
        bbox_obj.scale = bbox_dimensions * 0.5  # Cube is size 1, so scale by half dimensions

        # Parent to bone with offset
        bbox_obj.parent = armature
        bbox_obj.parent_type = 'BONE'
        bbox_obj.parent_bone = primary_bone
        bbox_obj.matrix_parent_inverse = armature.matrix_world.inverted()

        # Add physics properties for Cannon.js
        bbox_obj["physics_type"] = "rigidBody"
        bbox_obj["collider_shape"] = "box"
        bbox_obj["mass"] = 1.0


def get_primary_bone_name(obj):
    """Determine the primary bone name based on vertex group weights"""
    if not obj.vertex_groups:
        return None

    weight_sums = {vg.name: 0.0 for vg in obj.vertex_groups}
    vert_count = {vg.name: 0 for vg in obj.vertex_groups}

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='OBJECT')

    for vert in obj.data.vertices:
        for group in vert.groups:
            vg_name = obj.vertex_groups[group.group].name
            weight_sums[vg_name] += group.weight
            vert_count[vg_name] += 1

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
    bone_names = [b.name for b in armature.data.bones]

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    original_groups = {vg.name: vg.index for vg in obj.vertex_groups}

    with bpy.context.temp_override(active_object=obj):
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        for bone_name in bone_names:
            if bone_name not in original_groups:
                continue

            bpy.ops.mesh.select_all(action='DESELECT')
            obj.vertex_groups.active_index = original_groups[bone_name]
            bpy.ops.object.vertex_group_select()

            if not any(v.select for v in bm.verts):
                continue

            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.separate(type='SELECTED')

        bpy.ops.object.mode_set(mode='OBJECT')

    separated_objects = [o for o in bpy.context.selected_objects if o != obj]
    for new_obj in separated_objects:
        primary_bone = get_primary_bone_name(new_obj)

        for vg in new_obj.vertex_groups[:]:
            if vg.name != primary_bone:
                new_obj.vertex_groups.remove(vg)

        if primary_bone:
            new_obj.name = f"{primary_bone}_MESH"

        if 'Armature' not in new_obj.modifiers:
            mod = new_obj.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = armature

        # Parent to armature
        new_obj.parent = armature
        new_obj.matrix_parent_inverse = armature.matrix_world.inverted()

    # Hide original
    obj.hide_set(True)
    obj.hide_render = True
