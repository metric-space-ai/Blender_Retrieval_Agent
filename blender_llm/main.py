from enum import StrEnum

from agent_lib.agent import Agent #needs system path append
import prompts

class ResponseTypes(StrEnum):
    CODE = "code"
    FAIL = "fail"
    REQUEST_SCENE_DESCRIPTION = "request_scene_description"
    REQUEST_OBJECTS_LIST = "request_objects_list"

response_dict = {"type": ResponseTypes, "content": str, "message": str}

code_generator_agent = Agent(
    model="gpt-4o",
    system_prompt=prompts.SYSTEM_PROMPT,
    response_template=response_dict,
    allowed_api_calls_per_prompt=3
)