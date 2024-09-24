class StrategyGeneratorAgent:
    def __init__(self) -> None:
        self.conversation = [
            {"role": "system", "content":
                """Your task is to generate strategy for creating a python script to be used in Blender 3D, you are provided with scene file that contains CAD model of a part, machine or device, all sub-parts should be in it.
                Create the strategy in form of numbered list, keep the list short, it can't have more than 8 points. Don't write any code yet, you are creating rough sketch that will be handle to developer that will do it.
                Keep in mind the following guidelines:
                -blender will be running as python module
                -all data to be visualized must be passed with the prompt itself as a text an will be hardcoded in the script
                -the goal is to create a class called BlenderModelMenager that will be runned inside a Flask app, developer will be supplied with templat of that class, that already contains methods for rendering videos(_generate_video()) and image (_generate_image()), that must the be last step in the strategy. 
                -no liblaries can be imported, here is a list of liblaries that are already imported and can be used: numpy, bpy, random, datetime, math, mathutils
                -don't explain yourself make only the strategy.
                -don't talk about structure of the script, docummentation, testing, integration, quality checks etc. 
                -everything must be done with python Blender api, don't give any tasks to be done with Blender UI. 
                -don't adjust lighthing in the scene, focus on the task.
                -object used for visualisation should be simple, preferable placed over the objects that already exist
                -keep the application simple overall, don't overcomplicate stuff
                -don't change render settings, resolution and animation length, animation always takes 100 frames
                
                The goal should be in your output on top of the list same as in the examples. 
                
                Here are a few example strategies for you:
                
                Goal: Visualize vibration energy [12.5, 10.4, 5.8, 3.67, 87.4, 15.4, 9.6]  that corresponds to object xby.56.1

                1. Get the object xby.56.1 by name and assert it exists, determine its geometrical center and find its bounding-box
                2. Add a cube with new material, to visualize object bounding-box, make the material half transparent, and with controllable color.
                3. Get median value of the given data to get a vibration base level.
                4. Using the base level animate the color of the new cube corresponding to the data, keeping in mind total length of the animation. 
                5. Point the camera towards object’s geometrical center, make sure that cube is visible in the camera, if not get distance to it and adjust the camera clip value to make it show.
                6. Call method _generate_video() to render a video 
                
                Goal: Find object 345.767.by in Blender file and show it on a render.

                1. Get the object xby.56.1 by name and assert it exists, determine its geometrical center and find its bounding-box
                2. Move the camera, along X,Z axis while keeping Y axis intact, to the object’s geometrical center and point camera towards it.
                3. Set the camera focal length to have 90 percent of object’s bounding-box in camera bounds. Focal length must remain in 26mm to 120mm range, if necessary move the camera back. Make sure that object is visible in the camera, if not get distance to it and adjust the camera clip value to make it show.
                4. Call method _generate_image() to render an image
                """
            },
        ]
    
    def generate_strategy(self, user_prompt):
        self.conversation.append({"role": "user", "content": user_prompt})
        
        completion = client.chat.completions.create(
            model=openai_model,
            messages=self.conversation
        )

        strategy = completion.choices[0].message.content
        self.conversation.append({"role": "system", "content": strategy})
        
        return strategy
    
    def dump_conversation(self):
        with open('strategy_generator_conversation.json', 'w') as output_file:
            json.dump(self.conversation, output_file, indent=2)