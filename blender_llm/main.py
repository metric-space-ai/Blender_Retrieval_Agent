from enum import StrEnum

from agent_lib.agent import Agent
import prompts
import agent_lib.utils 
from blender_scene import BlenderScene

def generated_code_handler(generated_code):
    if agent_lib.utils.static_code_check(generated_code) is None: #no issues
        if agent_lib.utils.try_to_run_code(generated_code) is None: #code worked
            

class ResponseTypes(StrEnum):
    CODE = "code"
    FAIL = "fail"
    REQUEST_SCENE_DESCRIPTION = "request_scene_description"
    REQUEST_OBJECTS_LIST = "request_objects_list"

response_dict = {"type": ResponseTypes, "content": str, "message": str}

scene_path = ""

code_generator_agent = Agent(
    model="gpt-4o",
    system_prompt=prompts.MAIN_SYSTEM_PROMPT,
    response_template=response_dict,
    allowed_api_calls_per_prompt=3
)


scene = BlenderScene(scene_path)

user_prompt = ""

agent_responsce_dict, _ = code_generator_agent.inference(prompt=user_prompt)

if agent_responsce_dict["ResponseTypes"] == "code":
    code_generator_agent(agent_responsce_dict["CODE"])