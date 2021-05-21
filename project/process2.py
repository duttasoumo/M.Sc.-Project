import time

import serial

ser = serial.Serial('COM7', 9600)
while (1):
    data = (ser.readline()).decode('UTF-8')
    print(data)
    time.sleep(1)
