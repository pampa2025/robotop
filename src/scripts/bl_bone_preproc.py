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


# Okay, let's tackle this problem. The user mentioned that after running the script, some child bones are inheriting the parent bone's name in their separated meshes. That's not good because each mesh part should correspond to its specific bone.

# First, I need to figure out why the child bones are getting the parent's name. The previous script might be incorrectly assigning the mesh names based on vertex groups that include multiple bones. Maybe when separating the mesh, vertices influenced by child bones are still part of the parent's vertex group, causing the parent's name to be used.

# I should check how the script determines which bone name to use for each separated mesh. The script probably loops through each bone's vertex group, selects those vertices, and separates them. However, if a vertex is part of multiple groups(like parent and child bones), it might end up in the wrong mesh.

# To fix this, I need to ensure that each vertex is only associated with one bone. The script should prioritize the most influential bone for each vertex. That way, when separating, each vertex belongs to exactly one bone's mesh.

# I'll modify the script to clean up the vertex groups before separation. For each new mesh part, remove all vertex groups except the one with the highest weight influence on those vertices. This ensures that each mesh part is correctly named after its dominant bone.

# Also, when naming the mesh objects, the script should check all vertex groups of the new object and find the one with the maximum average weight. That bone's name will be used for the mesh, preventing parent names from overriding child names.

# Another consideration is the bone hierarchy. Child bones might have vertices that are also influenced by their parents. The script needs to handle weight painting properly, ensuring that vertices are assigned to the correct bone based on their primary influence.

# Testing this approach in Blender, I can run the script on a test model where parent and child bones have overlapping vertex groups. After running, each separated mesh should have the correct bone name, even for child bones.


# Key Improvements:

# Primary Bone Detection: Uses vertex weight dominance to determine the true associated bone

# Accurate Naming: Names meshes after the bone with highest average weight influence

# Clean Vertex Groups: Removes all non-primary bone groups from each mesh part

# Hierarchy Preservation: Maintains proper parent-child relationships through matrix parenting


# Verification Steps in Blender:

# Select a separated mesh part

# Check:

# Only 1 vertex group exists matching the mesh name

# Vertex group weights are > 0 only for that bone

# Armature modifier points to original armature

# Transform hierarchy matches the bone's position

# This version ensures child bones get their own mesh parts named correctly, even if they share vertices with parent bones in the original model.
