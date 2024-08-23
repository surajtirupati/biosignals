from neurosity import NeurositySDK
from dotenv import load_dotenv
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

LEFT_THRESH = 0.75
RIGHT_THRESH = 0.75

data_left = {}
data_right = {}

index_left = 0
index_right = 0

def callback_left(data):
    global index_left
    data_left[index_left] = data
    print("data: ", data)
    index_left += 1


def callback_right(data):
    global index_right
    data_right[index_right] = data
    print("data: ", data)
    index_right += 1

def terminate():
    pass


if __name__ == '__main__':
    unsubscribe = neurosity.kinesis("leftArm", callback_left)

    key_bool = False

    while not key_bool:
        if data_left[index_left]['confidence'] > LEFT_THRESH:
            print('Left')
            # do something
            pass

        if terminate():
            key_bool = True


