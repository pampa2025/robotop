import bpy
import bmesh
from mathutils import Vector


def get_primary_bone_name(obj):
    """Determine primary bone based on vertex group weights"""
    if not obj.vertex_groups:
        return None

    weight_sums = {vg.name: 0.0 for vg in obj.vertex_groups}
    vert_count = {vg.name: 0 for vg in obj.vertex_groups}

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


def create_hitbox(obj):
    """Create physics hitbox as child object"""
    # Calculate world-space bounding box
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    min_co = Vector((
        min(c.x for c in bbox_corners),
        min(c.y for c in bbox_corners),
        min(c.z for c in bbox_corners)
    ))

    max_co = Vector((
        max(c.x for c in bbox_corners),
        max(c.y for c in bbox_corners),
        max(c.z for c in bbox_corners)
    ))

    dimensions = max_co - min_co
    center = (min_co + max_co) / 2

    # Create hitbox cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    hitbox = bpy.context.active_object
    hitbox.name = f"{obj.name}_HITBOX"
    hitbox.scale = dimensions

    # Parent to mesh part
    hitbox.parent = obj
    hitbox.matrix_parent_inverse = obj.matrix_world.inverted()

    # Configure display properties
    hitbox.display_type = 'BOUNDS'
    hitbox.hide_render = True
    hitbox["physics_type"] = "hitbox"

    return hitbox


def process_mesh(obj):
    # Get armature modifier
    armature_mod = next((mod for mod in obj.modifiers if mod.type == 'ARMATURE' and mod.object), None)
    if not armature_mod:
        return

    armature = armature_mod.object
    original_name = obj.name
    bone_names = [b.name for b in armature.data.bones]

    # Apply transforms
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Store original vertex groups
    original_groups = {vg.name: vg.index for vg in obj.vertex_groups}

    with bpy.context.temp_override(active_object=obj):
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        # Separate by bone vertex groups
        for bone_name in bone_names:
            if bone_name not in original_groups:
                continue

            # Select vertices
            bpy.ops.mesh.select_all(action='DESELECT')
            obj.vertex_groups.active_index = original_groups[bone_name]
            bpy.ops.object.vertex_group_select()

            if not any(v.select for v in bm.verts):
                continue

            # Duplicate and separate
            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.separate(type='SELECTED')

        bpy.ops.object.mode_set(mode='OBJECT')

    # Process separated parts
    separated_objects = [o for o in bpy.context.selected_objects if o != obj]
    for new_obj in separated_objects:
        # Clean vertex groups
        primary_bone = get_primary_bone_name(new_obj)
        for vg in new_obj.vertex_groups[:]:
            if vg.name != primary_bone:
                new_obj.vertex_groups.remove(vg)

        # Rename and parent
        if primary_bone:
            new_obj.name = f"{primary_bone}_MESH"

        if 'Armature' not in new_obj.modifiers:
            mod = new_obj.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = armature

        new_obj.parent = armature
        new_obj.matrix_parent_inverse = armature.matrix_world.inverted()

        # Create physics hitbox
        # Add armature modifier to hitbox and bind to bone
        hitbox = create_hitbox(new_obj)
        if primary_bone:
            mod = hitbox.modifiers.new(name="Armature", type='ARMATURE')
            mod.object = armature
            bone_constraint = hitbox.constraints.new(type='CHILD_OF')
            bone_constraint.target = armature
            bone_constraint.subtarget = primary_bone

    # Hide original
    obj.hide_set(True)
    obj.hide_render = True


# Execute processing
for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        process_mesh(obj)

print("Processing complete! Physics hitboxes created.")
