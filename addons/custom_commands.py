bl_info = {
    "name": "Custom Commands",
    "category": "Development",
    "blender" : (2, 80, 0)
}

import bpy
from bpy_extras.image_utils import load_image

def set_shading():
    for area in bpy.context.screen.areas: 
        if area.type == 'VIEW_3D':
            for space in area.spaces: 
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'

# reset scale and rotations
def reset_scale_and_rotations(obj):
    obj.select_set(True)
    #obj.rotation_euler = [0, 0, 0]
    obj.scale = (1.0, 1.0, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
def replaceTextureLink(obj):
    nodes = obj.active_material.node_tree.nodes.values()
    texture_node = obj.active_material.node_tree.nodes['Image Texture']
    
    #print(obj.active_material.node_tree.nodes['UV Map'])
    
    bImg = load_image("D:\\Develop\\Unity\\cat\\Assets\\Models\\Textures\\SimpleInteriorsHouses.png")
    
    texture_node.image = bImg
    
def addUVMapNode(obj):
    
    node_tree = obj.active_material.node_tree
    
    shader_node = node_tree.nodes.new("ShaderNodeUVMap")
    
    shader_node.location = (-700, 340)
    
    
    # Create second UV layer
    new_uv_layer = obj.data.uv_layers.new()
    
    obj.data.uv_layers.active = new_uv_layer
    
    new_uv_layer.active_render = True
    
    shader_node.uv_map = new_uv_layer.name
    
    # Link the two notes together    
    texture_node = node_tree.nodes['Image Texture']
    
    node_tree.links.new(texture_node.inputs[0], shader_node.outputs[0])
    
def addDetailColorMask(obj):
    image = bpy.data.images.new("DetailColorMask", width=1024, height=1024)
    
    image.filepath_raw = bpy.path.abspath('//DetailColorMask.png')
    image.file_format = 'PNG'
    image.save()


def op():
    bpy.ops.object.mode_set(mode='OBJECT')

    for obj in bpy.context.scene.objects.values():    
        reset_scale_and_rotations(obj)
        pass

    set_shading()
    
    active_obj = bpy.context.view_layer.objects.active 
    
    replaceTextureLink(active_obj)
    
    addUVMapNode(active_obj)
    
    addDetailColorMask(active_obj)

    
class ResetImportState(bpy.types.Operator):
    """Reset Import State"""
    bl_idname = "dev.reset_import_state"
    bl_label = "Reset Import State"
    bl_options = {'REGISTER', 'UNDO'}

    #total: bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def execute(self, context):
        op()

        return {'FINISHED'}    
    
    
class DevMenu(bpy.types.Menu):
    bl_label = "Dev Menu"
    bl_idname = "OBJECT_MT_dev_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator(ResetImportState.bl_idname)


def menu_func(self, context):
    self.layout.operator(ResetImportState.bl_idname)

    
def draw_item(self, context):
    layout = self.layout
    layout.menu(DevMenu.bl_idname)
    
    
def register():
    bpy.utils.register_class(ResetImportState)
    bpy.utils.register_class(DevMenu)
    
    bpy.types.TOPBAR_MT_edit.append(menu_func)
    
    bpy.types.INFO_HT_header.append(draw_item)

def unregister():
    bpy.utils.unregister_class(DevMenu)
    bpy.utils.unregister_class(ResetImportState)

    bpy.types.TOPBAR_MT_edit.remove(menu_func)    
    bpy.types.INFO_HT_header.remove(draw_item)
    
if __name__ == "__main__":
    register()