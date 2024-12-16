# Clown Pass Generator

Easily add a clown pass to your current scene. If you are into old school compositing or are forced to use the Adobe Suite and can't install the cryptomatte plugin, this might help you ! 
This addon can generate two types of clown passes, material and objects.

## Clown pass for objects in scene

![An example of the clown pass for objects in blender scene. ](https://raw.githubusercontent.com/Maxiriton/images_repo/refs/heads/main/clown_aov/clown_object.jpg)
## Clown pass for materials in scene

![An example of the clown pass for materials in blender scene. ](https://raw.githubusercontent.com/Maxiriton/images_repo/refs/heads/main/clown_aov/clown_material.jpg)

## Usage

### Clown Pass Generation

To add the clown pass, simply click on the **Object** Menu in Object Mode and click on the **Generate Clown Pass** button.  
![The Generate button is added at the bottom of the Object Menu ](https://raw.githubusercontent.com/Maxiriton/images_repo/refs/heads/main/clown_aov/generate_button.jpg)

You can adjust some parameters in the last operator panel in the **bottom left** corner of the 3D view.

![Parameters can be changed from the last operator Panel](https://raw.githubusercontent.com/Maxiriton/images_repo/refs/heads/main/clown_aov/UI.jpg)

And that's it you now have a clown pass added to your render.  If you are using Eevee, you can visualize the pass directly in the viewport. In Cycles, you need to render the image to have access to the new render pass. 

### Multipasses generation

By default, the addon generates a single pass where all colors are splated together. However sometimes it can be useful to have each color in its own pass. To do so, simply uncheck the **Is Monopass** option when you generate the clown pass.

### Automatic compositing setup

The addon comes with a compositing operator that automatically connects clown passes to an output node that will save the clow pass image on disc at an user defined folder. It is particularly usefull if you have selected to the multipasses option. Click on the **Setup Clown Passes** in the **Node** menu. A file browser will ask you for a target folder and upon validation, the addon connects clown passes to outputs images. 

![The Generate button is added at the bottom of the Object Menu ](https://raw.githubusercontent.com/Maxiriton/images_repo/refs/heads/main/clown_aov/generate_outputs.jpg)

### Removing the clown pass

If you want to remove the clown, call the specific operator from the **F3** Menu and search **Remove Clown**. 
