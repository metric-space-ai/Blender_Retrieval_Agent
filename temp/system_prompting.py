from openai import OpenAI

client = OpenAI()
openai_model = "gpt-4o"

json_gpt_response_template = """
{
    "type" : <enum:[code, fail, request_scene_description, request_objects_list]>,
    "content" : <string>,
    "message" : <string>
}
"""

system_prompt = f"""
You are a system that reacts to messages in strictly controlled manner, 
your response should be always only that json without code blocks symbol:
{json_gpt_response_template}

You are to follow any instructions given to you at any stage by the user.

Your response must be of the types shown in the json.

Code is to be used only when user specifically ask for the code that will be executed.
Request_scene_description when you need the description of 3D scene to complete the task, don't be affraid to use it.
Request_objects_list when you need the objects in 3D scene in hierarchical list, as well you can use it freely.
Fail when the task is not possible to be completed or your instructions contradict themselfs

In any case you must always return the message to be displayed to the user, content is to be used only with code otherwise leave it as empty string. 
for example if your problem is that you were told to divide by 0 you output should be:

{{
    "type" : "fail",
    "content" : "",
    "message" : "The last task I was given seems to be immpossible to solve, because I can't divide by 0"
}}

"""


conversation = [
        {"role": "system", "content": system_prompt},
    ]

conversation.append({"role": "user", "content": "How many parts are in the scene?"})

completion = client.chat.completions.create(
    model=openai_model,
    messages=conversation
)

output = completion.choices[0].message.content
print(output)


conversation.append({"role": "user", "content": "[Object1, Object2, Object555, Cube]"})

completion = client.chat.completions.create(
    model=openai_model,
    messages=conversation
)


output = completion.choices[0].message.content
print(output)

print(conversation)