import bpy
import uuid
from enum import StrEnum
import logging
import json

import blender_utils
from agent_lib.agent import Agent, VisionAgent
import prompts

logger = logging.getLogger(__name__)


class BlenderSceneNotFound(Exception):
    "Raise when the blender scene is not found, while trying to open it"


class BlenderScene:
    def __init__(self, scene_file_name):
        try:
            bpy.ops.wm.open_mainfile(filepath=scene_file_name)
        except Exception as e:
            raise BlenderSceneNotFound from e
        logger.info(f"Loaded blender scene {scene_file_name}")

        renders_description_agent = VisionAgent(
            model="gpt-4o",
            system_prompt=prompts.VISION_IMAGE_DESCRIPTION_SYSTEM_PROMPT,
        )
        
        scene_description_agent = Agent(
            model="gpt-4o",
            system_prompt=prompts.SCENE_DESCRIPTION_SYSTEM_PROMPT,
        )


        self.hierarchy_string = blender_utils.get_all_objects_hierarchy()
        raw_scene_info_dict = blender_utils.get_scene_static_info()

        self.cameras_renders_description = []
        camera_list = raw_scene_info_dict["cameras"]
        camera_list = camera_list[:4]

        for camera in camera_list:
            render_filename = str(uuid.uuid4())
            blender_utils.render_image(render_filename, camera)
            render_description, _ = renders_description_agent.inference(
                prompt=prompts.RENDER_DESCCRIPTION_PROMPT, image_path=render_filename
            )
            self.cameras_renders_description.append((camera, render_description))
            renders_description_agent.clear_converstation()


        scene_info_string = json.dumps(raw_scene_info_dict)

        self.scene_description = scene_description_agent.inference(
            scene_info_string
        )
