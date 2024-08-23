from neurosity import NeurositySDK
from dotenv import load_dotenv
import time
import os
import json
from eeg.scripts.utils import convert_timestamp_ms_to_time

load_dotenv()

#  Inputs
TITLE = 'ChillinLikaVillain'
TOTALTIME = 30

# Logging into Neurosity
neurosity = NeurositySDK({
    "device_id": os.getenv("NEUROSITY_DEVICE_ID"),
})

neurosity.login({
    "email": os.getenv("NEUROSITY_EMAIL"),
    "password": os.getenv("NEUROSITY_PASSWORD")
})

data_returned = {}

index = 0


def callback(data):
    global index
    data_returned[index] = data
    print("data: ", data)
    index += 1


start_time_milliseconds = time.time() * 1000
start_datetime = convert_timestamp_ms_to_time(start_time_milliseconds)
unsubscribe = neurosity.brainwaves_raw_unfiltered(callback)

time.sleep(TOTALTIME)

unsubscribe()
end_time_milliseconds = time.time() * 1000
end_datetime = convert_timestamp_ms_to_time(end_time_milliseconds)

with open(f'../files/unfiltered/{TITLE}.json', 'w') as json_file:
    json.dump(data_returned, json_file, indent=4)

first_sample_time = convert_timestamp_ms_to_time(data_returned[0]['info']['startTime'])
last_sample_time = convert_timestamp_ms_to_time(data_returned[len(data_returned) - 1]['info']['startTime'])

print(f"Start of Code Time: {start_datetime}\nFirst Sample Time: {first_sample_time}\nLast Sample Time: {last_sample_time}\nEnd of Code Time: {end_datetime}")

print()
