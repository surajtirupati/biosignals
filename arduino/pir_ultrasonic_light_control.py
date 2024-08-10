import serial
import time

from hue.hue import bridge


# Replace 'COM3' with the correct port for your Arduino.
# On Windows, it will be something like 'COM3', 'COM4', etc.
# On Linux or Mac, it will be something like '/dev/ttyUSB0', '/dev/ttyACM0', etc.
arduino_port = 'COM3'
baud_rate = 9600  # Must match the baud rate in the Arduino code
off = True
prev_pir = 0
ultra_thresh = 20

# Create a serial connection to the Arduino
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)  # Give some time for the connection to establish

print("Connected to Arduino at " + arduino_port)

try:
    while True:
        if ser.in_waiting > 0:
            # Read the serial data and decode it to string
            line = ser.readline().decode('utf-8').strip()
            pir_value, us_val = int(line.split(',')[0]), int(line.split(',')[1])
            print(f'PIR value: {pir_value}')
            print(f'Distance: {us_val}')
            print(f'Off: {off}')
            print('\n\n')

            if pir_value == 1 and off and prev_pir == 0 and us_val < ultra_thresh:
                bridge.run_scene('SJ Bedroom', 'Arise')
                off = False
                prev_pir = pir_value

            elif pir_value == 1 and not off and prev_pir == 0 and us_val < ultra_thresh:
                bridge.run_scene('SJ Bedroom', 'Sleepy')
                off = True
                prev_pir = pir_value

            else:
                prev_pir = pir_value


except KeyboardInterrupt:
    print("Exiting program")

finally:
    ser.close()
