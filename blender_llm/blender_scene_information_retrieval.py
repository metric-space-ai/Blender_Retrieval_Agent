import bpy
import uuid
from enum import StrEnum
import logging

import blender_utils
from agent_lib.agent import Agent
import prompts

logger = logging.getLogger(__name__)

class BlenderSceneNotFound(Exception):
    "Raise when the blender scene is not found, while trying to open it"

def get_all_scene_raw_data(scene_file_name: str):
    
    try:
        bpy.ops.wm.open_mainfile(filepath=scene_file_name)
    except Exception as e:
        raise BlenderSceneNotFound from e 
        
    hierarchy_string = blender_utils.get_all_objects_hierarchy()
    raw_scene_info_dict = blender_utils.get_scene_static_info()
    
    images_cameras =[]
    
    for camera in raw_scene_info_dict["cameras"]:
        image_filename = str(uuid.uuid4())
        blender_utils.render_image(image_filename, camera)
        images_cameras.append((camera, image_filename))
        
    return hierarchy_string, raw_scene_info_dict, images_cameras

def get_final_scene_description_and_data(scene):
    
    scene_description_agent = Agent(
        model="gpt-4o",
        system_prompt=prompts.SCENE_DESCRIPTION_SYSTEM_PROMPT,
    )
    
    hierarchy_string, scene_info_dict, renders_cameras = get_all_scene_raw_data(scene)