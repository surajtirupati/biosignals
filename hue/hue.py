from dotenv import load_dotenv
import phue
import os

load_dotenv()

bridge = phue.Bridge(os.getenv("PHUE_IP_ADDRESS"))
bridge.connect()

go = bridge.lights[0]
table = bridge.lights[1]
floor = bridge.lights[2]
