# To make this add-on installable, create an extension with it:
# https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty, EnumProperty
from mathutils import Vector, Color

from colorsys import hsv_to_rgb

AOV_NODE_NAME = 'Clown AOV'
AOV_NAME = 'Clown'
AOV_COLOR_ATTR_NODE_NAME = 'AOV Color Attribute'
ATTR_NAME = 'clown_color'
CUSTOM_PROPERTY_NAME = 'clown_color_attributes'


def get_filtered_objects(context, types= ['CAMERA','LIGHT','NONE','EMPTY']): 
    return  [obj for obj in context.scene.objects if obj.type not in types and obj.users > 0]

def clean_up_previous_aov(self, context):
    '''Utility function that remove all aspects of clown AOV in the current scene. 
       This is call before creating clown or by its own operator'''
    
    #cleaning up materials
    for mat in bpy.data.materials:
        if not mat.node_tree:
            continue
        aov_nodes = [node for node in mat.node_tree.nodes if node.name.startswith(AOV_NAME)]

        for node in reversed(aov_nodes):
            mat.node_tree.nodes.remove(node)

        #cleaning material custom properties
        custom_prop = mat.get(CUSTOM_PROPERTY_NAME)
        if custom_prop:
            print('on a trouvé une custom prop')
            del mat[CUSTOM_PROPERTY_NAME]

    #cleaning up mesh attributes
    for obj in get_filtered_objects(context):
        mesh = obj.data
        for attrib in reversed(mesh.attributes):
            if attrib.name.startswith(ATTR_NAME):
                mesh.attributes.remove(attrib)

    #cleaning up AOV list
    aovs_to_remove = [aov for aov in context.view_layer.aovs if aov.name.startswith(AOV_NAME)]
    for aov in reversed(aovs_to_remove):
        context.view_layer.aovs.remove(aov)

    #cleaning up compositing tree
    #TODO

def generate_material_clown_aov(self, context):
    nb_mat = len([mat for mat in bpy.data.materials if mat.users > 0])
    hue_interval = 1 / nb_mat

    for index, mat in enumerate(bpy.data.materials):
        if mat.node_tree is None:
            continue

        frame_node = mat.node_tree.nodes.new('NodeFrame')
        frame_node.location = Vector((400, -130))
        frame_node.name = f"{AOV_NAME}_frame"
        frame_node.label = "Clown Pass AOV setup"

        aov_node = mat.node_tree.nodes.new('ShaderNodeOutputAOV')
        aov_node.name = AOV_NODE_NAME

        color = Color()
        color.hsv = hue_interval * index, 1 ,1 
        r, g, b = hsv_to_rgb(color.h, color.s, color.v)

        aov_node.inputs[0].default_value = Vector((r, g, b, 1))
        aov_node.location = Vector((400,-130))
        aov_node.parent = frame_node
        if self.is_monopass: 
            aov_node.aov_name = AOV_NAME
        else:
            aov_node.aov_name = f"{AOV_NAME}_{index}"
            aov_pass = context.view_layer.aovs.add()
            aov_pass.name = f"{AOV_NAME}_{index}"

    if self.is_monopass:
        aov_pass = context.view_layer.aovs.add()
        aov_pass.name = AOV_NAME

def generate_object_clown_aov(self, context):
    filtered_objects = get_filtered_objects(context)
    hue_interval = 1 / len(filtered_objects)

    for index, obj in enumerate(filtered_objects):
        color = Color()
        color.hsv = hue_interval * index, 1 ,1 
        r, g, b = hsv_to_rgb(color.h, color.s, color.v)

        mesh = obj.data
        attribute = mesh.attributes.get(ATTR_NAME)
        if attribute is None:
            name = ATTR_NAME if self.is_monopass else f"{ATTR_NAME}_{obj.name}"
            attribute = mesh.attributes.new(name=name , type="FLOAT_COLOR", domain="FACE")
        attribute_values = [r, g, b, 1]  * len(mesh.polygons)
        attribute.data.foreach_set("color", attribute_values)

        for mat in [matslot.material for matslot in obj.material_slots if matslot.material is not None]:
            if mat.node_tree is None:
                continue

            nb_of_attributes = mat.get(CUSTOM_PROPERTY_NAME)
            if nb_of_attributes is None:
                nb_of_attributes = mat[CUSTOM_PROPERTY_NAME] = 0
                frame_node = mat.node_tree.nodes.new('NodeFrame')
                frame_node.location = Vector((400, -130))
                frame_node.name = f"{AOV_NAME}_frame"
                frame_node.label = "Clown Pass AOV setup"

            frame_node = mat.node_tree.nodes[f"{AOV_NAME}_frame"]


            if self.is_monopass:
                attr_node = mat.node_tree.nodes.new("ShaderNodeAttribute")
                attr_node.name = f"{AOV_NAME}_attr"
                attr_node.attribute_name = ATTR_NAME
                attr_node.parent = frame_node

                aov_node = mat.node_tree.nodes.new('ShaderNodeOutputAOV')
                aov_node.name = AOV_NODE_NAME
                aov_node.aov_name = AOV_NAME
                aov_node.parent = frame_node

                mat.node_tree.links.new(attr_node.outputs[0], aov_node.inputs[0])
            else:
                attr_node = mat.node_tree.nodes.new("ShaderNodeAttribute")
                attr_node.name = f"{AOV_NAME}_attr_{obj.name}"
                attr_node.attribute_name = f"{ATTR_NAME}_{obj.name}"
                attr_node.parent = frame_node

                aov_node = mat.node_tree.nodes.new('ShaderNodeOutputAOV')
                aov_node.name =f"{AOV_NAME}_{obj.name}"
                aov_node.aov_name = f"{AOV_NAME}_{obj.name.replace('.','_')}"
                aov_node.parent = frame_node

                mat.node_tree.links.new(attr_node.outputs[0], aov_node.inputs[0])

                aov_pass = context.view_layer.aovs.add()
                aov_pass.name = f"{AOV_NAME}_{obj.name}"

            attr_node.location = Vector((400,-200 * nb_of_attributes))
            aov_node.location = Vector((650,-200 * nb_of_attributes))
            mat['clown_color_attributes'] += 1


    if self.is_monopass:
        aov_pass = context.view_layer.aovs.add()
        aov_pass.name = AOV_NAME

class CLOWN_setup_compositor(Operator):
    bl_idname = "clown.setup_compositor"
    bl_label = "Setup clown passes outputs"
    bl_description = "Setup clow passes output"
    bl_options = {"REGISTER", "UNDO"}

    # Define this to tell 'fileselect_add' that we want a directoy
    directory: StringProperty(
        name="Outdir Path",
        description="Where I will save my stuff"
        # subtype='DIR_PATH' is not needed to specify the selection mode.
        # But this will be anyway a directory path.
        )

    # Filters folders
    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}
        )

    def execute(self, context):
        render_layers_node = context.scene.node_tree.nodes.get('Render Layers')
        if render_layers_node is None:
            return {'CANCELED'}
        
        for output in render_layers_node.outputs:
            if not output.name.startswith(AOV_NAME):
                continue

            output_node = context.scene.node_tree.nodes.new("CompositorNodeOutputFile")
            output_node.base_path = self.directory

            context.scene.node_tree.links.new(output, output_node.inputs[0])
            

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class CLOWN_remove_aovs(Operator):
    bl_idname = "clown.remove_clown_aovs"
    bl_label = "Remove Clown Render Pass"
    bl_description ="Remove all data of clown pass in the scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        clean_up_previous_aov(self, context)
        return {"FINISHED"}



class CLOWN_generate_AOVs(Operator):
    bl_idname = "clown.generate_aov"
    bl_label = "Generate Clown Render Pass"
    bl_description = "Generate AOVs"
    bl_options = {"REGISTER", "UNDO"}

    clown_target: EnumProperty(
        name="Target",
        items=(
            ('OBJECTS', "Objects", ""),
            ('MATERIALS', "Materials", ""),
        ),
        description = "Apply Clown pass to materials instead of objects",
    )

    is_monopass : BoolProperty(
        name = "Monopass",
        description = "All clown colors are rendered on a single layer",
        default = True
    )


    def execute(self, context):
        #we clean up the scene
        clean_up_previous_aov(self, context)

        if self.clown_target == 'MATERIALS':
            generate_material_clown_aov(self, context)
        else:
            generate_object_clown_aov(self, context)

        return {"FINISHED"}


# Registration

def aov_button(self, context):
    self.layout.operator(
        CLOWN_generate_AOVs.bl_idname,
        text="Generate Clown Pass",
        icon='BRUSHES_ALL')

def clown_compositor(self, context):
    self.layout.operator(
        CLOWN_setup_compositor.bl_idname,
        text="Setup Clown passes",
        icon='BRUSHES_ALL')


def register():
    bpy.utils.register_class(CLOWN_generate_AOVs)
    bpy.utils.register_class(CLOWN_setup_compositor)
    bpy.utils.register_class(CLOWN_remove_aovs)
    bpy.types.VIEW3D_MT_object.append(aov_button)
    bpy.types.NODE_MT_node.append(clown_compositor)



def unregister():
    bpy.utils.unregister_class(CLOWN_generate_AOVs)
    bpy.utils.unregister_class(CLOWN_setup_compositor)
    bpy.utils.unregister_class(CLOWN_remove_aovs)
    bpy.types.VIEW3D_MT_object.remove(aov_button)
    bpy.types.NODE_MT_node.remove(clown_compositor)


if __name__ == "__main__":
    register()
