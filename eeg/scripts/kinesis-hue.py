from neurosity import NeurositySDK
from dotenv import load_dotenv
import random
import time
import phue
import os

load_dotenv()

# Logging into Neurosity
neurosity = NeurositySDK({
    "device_id": os.getenv("NEUROSITY_DEVICE_ID"),
})

neurosity.login({
    "email": os.getenv("NEUROSITY_EMAIL"),
    "password": os.getenv("NEUROSITY_PASSWORD")
})

bridge = phue.Bridge(os.getenv("PHUE_IP_ADDRESS"))
bridge.connect()

go = bridge.lights[0]
table = bridge.lights[1]
floor = bridge.lights[2]

groups = bridge.get_group()

# Print all available groups to find the one you want to use
for group_id, group in groups.items():
    print(f"Group ID: {group_id}, Name: {group['name']}")


# Get the list of scenes
scenes = bridge.get_scene()

# Print all available scenes to find the one you want to activate
scene_dict = {}
for scene_id, scene in scenes.items():
    print(f"Scene ID: {scene_id}, Name: {scene['name']}")
    scene_dict[scene['name']] = scene_id

# Define the group ID and scene ID you want to activate
# Replace these with the IDs from your bridge
group_id = 'SJ Bedroom'  # typically 1 for "all lights" group, or specific group ID
scene_name = ['Sleepy', 'Arise', 'Singapore']  # Replace with the desired scene ID

# Activate the scene
bridge.run_scene('SJ Bedroom', 'Sleepy')


while True:
    random_number = random.randint(0, 2)
    scene = scene_name[random_number]
    print(f"Setting Scene: {scene}")
    bridge.run_scene('SJ Bedroom', scene)
    time.sleep(2)


def callback(data):
    level = int(data['probability'] * 255)
    print(f'Brightness Level Table: {level}')
    table.brightness = level


def callback_two(data):
    level = int(data['probability'] * 255)
    print(f'Brightness Level Floor: {level}')
    table.brightness = level

def callback_three(data):
    level = int(data['probability'] * 255)
    print(f'Brightness Level Floor: {level}')
    floor.brightness = level


# unsubscribe = neurosity.kinesis_predictions("push", callback)
unsubscribe = neurosity.calm(callback_two)
unsubscribe = neurosity.focus(callback_three)



print()


