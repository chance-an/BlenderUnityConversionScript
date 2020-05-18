import bpy
import mathutils
from math import radians
from mathutils import Matrix

blender249 = True
blender280 = (2,80,0) <= bpy.app.version

try:
    import Blender
except:
    blender249 = False

if not blender280:
    if blender249:
        try:
            import export_fbx
        except:
            print('error: export_fbx not found.')
            Blender.Quit()
    else :
        try:
            import io_scene_fbx.export_fbx
        except:
            print('error: io_scene_fbx.export_fbx not found.')
            # This might need to be bpy.Quit()
            raise

# Find the Blender output file
import os
outfile = os.getenv("UNITY_BLENDER_EXPORTER_OUTPUT_FILE")

# Do the conversion
print("Starting blender to FBX conversion " + outfile)

if blender280:
    import bpy.ops

    override_context = bpy.context.copy()

    # deselect all objects
    for obj in bpy.context.scene.objects.values():
        override_context['active_object'] = obj
        bpy.ops.object.mode_set(override_context, mode='OBJECT')
        obj.select_set(False)
        
    # delete hidden objects
    hidden_objs = []
    for obj in bpy.context.scene.objects.values():
        if obj.visible_get() == False:
            obj.hide_set(False)
            obj.hide_select = False
            hidden_objs.append(obj)

    override_context = bpy.context.copy()
    override_context['selected_objects'] = hidden_objs
    bpy.ops.object.delete(override_context)

    # TODO: Apply modifiers
    # a) deactivate animation constraints
    # b) apply mirror modifiers


    matPatch = Matrix.Rotation(radians(-90.0), 4, 'X');
    #matPatch = matPatch @ Matrix.Rotation(radians(0), 4, 'X');

    # Rotate objects
    for obj in bpy.context.scene.objects.values():
        if obj.parent != None:
            continue  
        if obj.type == 'ARMATURE': # By default, the non-rotated Armature is correctly oriented
            continue
        obj.matrix_world = matPatch @ obj.matrix_world

    # Apply Rotation
    override_context = bpy.context.copy()
    for obj in bpy.context.scene.objects.values():
        if obj.hide_select:
            obj.hide_select = False
        obj.select_set(True)
        override_context['selected_objects'] = [obj]
        bpy.ops.object.transform_apply(rotation=True, location=True)
        obj.select_set(False)
    
    bpy.ops.export_scene.fbx(filepath=outfile,
        check_existing=False,
        use_selection=False,
        use_active_collection=False,
        object_types= {'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='OFF',
        use_custom_props=True,
        apply_scale_options='FBX_SCALE_ALL',
        bake_anim_simplify_factor=0.0
        )
elif blender249:
    mtx4_x90n = Blender.Mathutils.RotationMatrix(-90, 4, 'x')
    export_fbx.write(outfile,
        EXP_OBS_SELECTED=False,
        EXP_MESH=True,
        EXP_MESH_APPLY_MOD=True,
        EXP_MESH_HQ_NORMALS=True,
        EXP_ARMATURE=True,
        EXP_LAMP=True,
        EXP_CAMERA=True,
        EXP_EMPTY=True,
        EXP_IMAGE_COPY=False,
        ANIM_ENABLE=True,
        ANIM_OPTIMIZE=False,
        ANIM_ACTION_ALL=True,
        GLOBAL_MATRIX=mtx4_x90n)
else:
    # blender 2.58 or newer
    import math
    from mathutils import Matrix
    # -90 degrees
    mtx4_x90n = Matrix.Rotation(-math.pi / 2.0, 4, 'X')

    class FakeOp:
        def report(self, tp, msg):
            print("%s: %s" % (tp, msg))

    exportObjects = ['ARMATURE', 'EMPTY', 'MESH']

    minorVersion = bpy.app.version[1];
    if minorVersion <= 58:
        # 2.58
        io_scene_fbx.export_fbx.save(FakeOp(), bpy.context, filepath=outfile,
            global_matrix=mtx4_x90n,
            use_selection=False,
            object_types=exportObjects,
            mesh_apply_modifiers=True,
            ANIM_ENABLE=True,
            ANIM_OPTIMIZE=False,
            ANIM_OPTIMIZE_PRECISSION=6,
            ANIM_ACTION_ALL=True,
            batch_mode='OFF',
            BATCH_OWN_DIR=False)
    else:
        # 2.59 and later
        kwargs = io_scene_fbx.export_fbx.defaults_unity3d()
        io_scene_fbx.export_fbx.save(FakeOp(), bpy.context, filepath=outfile, **kwargs)
    # HQ normals are not supported in the current exporter

print("Finished blender to FBX conversion " + outfile)
