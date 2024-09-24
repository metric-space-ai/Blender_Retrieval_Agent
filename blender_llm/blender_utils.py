import bpy
from mathutils import Vector
import os
import time
import logging

logger = logging.getLogger(__name__)

def get_single_hierarchy(obj, level=0):
    "Recursively retrieves the hierarchy of objects starting from the given object."
    indent = "-" * (level + 1)
    result = f"{indent}{obj.name}\n"
    for child in obj.children:
        result += get_single_hierarchy(child, level + 1)
    return result


def get_all_objects_hierarchy():
    "Retrieves the hierarchical list of all objects in the current Blender scene."
    hierarchy_string = ""
    for obj in bpy.context.scene.objects:
        if obj.parent is None:  # Only include root objects
            hierarchy_string += get_single_hierarchy(obj, 0)
    return hierarchy_string


def get_scene_static_info():
    """
    Gathers information about the current Blender scene.

    This function counts the number of mesh objects in the scene,
    calculates the total vertex count for all mesh objects,
    determines a single bounding box that encompasses
    all mesh objects, and collects the names of all cameras in the scene.
    It also retrieves the scene's unit settings.

    Returns:
        dict: A dictionary containing the following keys:
            - 'object_count' (int): The number of mesh objects in the scene.
            - 'vertex_count' (int): The total number of vertices across all mesh objects.
            - 'bounding_box' (list): A list containing two vectors [min_corner, max_corner]
              representing the bounding box that contains all mesh objects, or None if no mesh objects exist.
            - 'cameras' (list): A list of names of all camera objects in the scene.
            - 'scene_units' (str): The units of measurement used in the scene (e.g., 'METRIC', 'IMPERIAL').
    """

    scene_info = {
        "object_count": 0,
        "vertex_count": 0,
        "bounding_box": None,
        "cameras": [],
        "scene_units": bpy.context.scene.unit_settings.system,  # Get the unit system
    }

    # Initialize bounding box with extreme values
    min_corner = Vector((float("inf"), float("inf"), float("inf")))
    max_corner = Vector((-float("inf"), -float("inf"), -float("inf")))

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            scene_info["object_count"] += 1
            scene_info["vertex_count"] += len(obj.data.vertices)

            # Update bounding box corners
            for v in obj.bound_box:
                world_coord = obj.matrix_world @ Vector(v)
                min_corner = Vector(min(min_corner, world_coord))
                max_corner = Vector(max(max_corner, world_coord))

        elif obj.type == "CAMERA":
            scene_info["cameras"].append(obj.name)

    # Create a single bounding box that contains all mesh objects
    if scene_info["object_count"] > 0:
        scene_info["bounding_box"] = [min_corner, max_corner]

    logger.info(f"Scene info gathered, scene raw info is: \n {scene_info}")
    
    return scene_info

def render_image(filename: str, camera_name: str):
    """
    Renders a single image in Blender using a specified camera and saves it to a file.
    
    Args:
        filename (str): The file path where the rendered image will be saved. 
                        Should include the file extension (e.g., 'render.png').
        camera_name (str): The name of the camera to use for rendering. It must match
                           the name of a camera object in the scene.
    
    Raises:
        AssertionError: If the specified camera is not found in the scene.
    """
    
    #Handle extension and no extension of the filename
    if filename.endswith(".jpg"):
        pass
    else:
        filename = filename + ".jpg"
    
    # Find the camera object by name
    camera = bpy.data.objects.get(camera_name)
    
    assert camera, f"Camera '{camera_name}' not found in the scene."
    
    # Set the active scene camera to the specified camera
    bpy.context.scene.camera = camera
    
    # Set the output file path
    bpy.context.scene.render.filepath = filename
    
    # Render the image
    bpy.ops.render.render(write_still=True)
    
    #wait for image to be save to the drive     
    while os.path.exists(filename) == False:
        time.sleep(2)
    
    logger.info(f"Rendered image saved to '{filename}' using camera '{camera_name}'")