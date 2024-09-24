# pylint: disable=W1203

import logging
import json
from enum import StrEnum
from openai import OpenAI

import constants
import utils

logger = logging.getLogger(__name__)
logging.basicConfig(filename=f"{__name__}.log", level=logging.INFO)


class LLMFaileToCreateValidJson(Exception):
    """Raise when LLM was not able to create valid json output and \
    was not able to correct itself within allowed api calls"""


class Agent:
    """
    A class to create and manage an AI agent that interacts with the OpenAI API.

    Attributes:
        model (str): The model used by the agent for inference.
        system_prompt (str): The initial prompt that sets the context for the conversation.
        response_template (dict): A template for validating the response format from the model.
        allowed_api_calls_per_prompt (int): The maximum number of API calls allowed per prompt to correct responses.
        openai_ai_token (str): The token for authenticating with the OpenAI API.
        client (OpenAI): An instance of the OpenAI client for making API calls.
        conversation (list): A list that stores the conversation history.
    """

    def __init__(
        self,
        model: str,
        system_prompt: str,
        response_template: dict = None,
        allowed_api_calls_per_prompt: int = 3,
        opena_ai_token: str = None,
    ):
        """
        Initializes an Agent instance.

        Args:
            model (str): The model to be used by the agent.
            system_prompt (str): The system prompt that guides the agent's behavior.
            response_template (dict, optional): A template to validate the response. Defaults to None.
            allowed_api_calls_per_prompt (int, optional): Number of API calls allowed for response correction. Defaults to 3.
            opena_ai_token (str, optional): Token for OpenAI API. Must be set as env variable if not provided. Defaults to None.
        """
        logger.info(f"Creating new agent for model: {model}")
        self.openai_model = model
        self.client = OpenAI()
        self.system_prompt = system_prompt
        self.conversation = [
            {"role": "system", "content": system_prompt},
        ]
        self.response_template = response_template
        self.allowed_api_calls_per_prompt = allowed_api_calls_per_prompt

    def inference(self, prompt: str):
        """
        Processes a user prompt and returns the agent's output along with the conversation history.

        Args:
            prompt (str): The user prompt to be processed.

        Returns:
            tuple: A tuple containing the raw output from the model (or converted output if a template is provided)
                   and the updated conversation history.
        """
        logger.info(f"Agent inference with prompt: {prompt}")
        self.conversation.append({"role": "user", "content": prompt})
        raw_output = self._complete()
        self.conversation.append({"role": "system", "content": raw_output})

        if self.response_template is None:
            return raw_output, self.conversation
        else:
            converted_output = self._check_load_fix_response(raw_output)
            return converted_output, self.conversation

    def dump_conversation(self, file_name: str):
        """
        Saves the conversation history to a JSON file.

        Args:
            file_name (str): The name of the file to save the conversation.
                             It can end with .json or don't have extension.
        """
        if file_name.endswith(".json"):
            file_name = file_name.split(".")[0]
        with open(f"{file_name}.json", "w") as output_file:
            json.dump(self.conversation, output_file, indent=2)

    def clear_converstation(self):
        """Cleares conversation back to system prompt only"""

        self.conversation = [
            {"role": "system", "content": self.system_prompt},
        ]

    def _complete(self):
        """
        Completes the current conversation by sending it to the OpenAI API and receiving a response.

        Returns:
            str: The content of the response from the model.
        """
        completion = self.client.chat.completions.create(
            model=self.openai_model, messages=self.conversation
        )
        chat_response = completion.choices[0].message.content
        return chat_response

    def _check_load_fix_response(self, response: str):
        """
        Validates and attempts to fix the response from the model, ensuring it conforms to the expected template.

        Args:
            response (str): The raw response from the model to be validated.

        Returns:
            dict: A valid JSON object that conforms to the response template.

        Raises:
            LLMFaileToCreateValidJson: If the response cannot be corrected within the allowed API calls.
        """
        i = 0
        while i < self.allowed_api_calls_per_prompt:
            try:
                output_dict = json.loads(response)
            except json.decoder.JSONDecodeError:
                i += 1
                logger.warning(
                    f"""LLM response not parsable as json, attempting to fix \
                    this prompt {i}/{self.allowed_api_calls_per_prompt} times"""
                )
                self.conversation.append(
                    {"role": "user", "content": constants.JSON_NOT_PARSABLE}
                )
                parsable_response = self._complete()
                response = parsable_response
                continue
            else:
                if utils.check_dict(self.response_template, output_dict) is True:
                    return output_dict
                else:
                    i += 1
                    logger.warning(
                        f"""LLM response was parsable as json, \
                        but didn't conform to provided template, \
                        attempting to fix this prompt: \
                        {i}/{self.allowed_api_calls_per_prompt} times"""
                    )
                    self.conversation.append(
                        {
                            "role": "user",
                            "content": constants.JSON_NOT_CONFORMING_TO_TEMPLATE,
                        }
                    )
                    parsable_response = self._complete()
                    response = parsable_response
                    continue

        logger.error(
            """LLM was not able to create requested json template \
            and was not able to correct itself within allowed api calls"""
        )
        raise LLMFaileToCreateValidJson
