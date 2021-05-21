import threading
import time

import RPi.GPIO as GPIO
import serial
from flask import Flask, render_template, request

# file1 = open("buffer.txt","r")
app = Flask(__name__)

PORT = "/dev/ttyACM0"
# PORT = "COM7"
LED = 7
EXHAUST = 11
PELTIER_FAN = 15
WATERP = 13
PELTIER = 16

GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(EXHAUST, GPIO.OUT)
GPIO.setup(PELTIER, GPIO.OUT)
GPIO.setup(PELTIER_FAN, GPIO.OUT)
GPIO.setup(WATERP, GPIO.OUT)

# GPIO.cleanup()

actuator_state = {'manual': False, 'exhaust': False, 'waterp': False, 'humidifier': False, 'light': False,
                  'peltier': False}

value = []
flag = 0

file_name = "buffer.txt"
temp_file = open(file_name, "r")
buffer = temp_file.readline().strip()
temp_file.close()


@app.route('/')
def index():
    return render_template('form.html')


@app.route('/process', methods=['POST'])
def process():
    global flag
    if flag == 0:
        if len(value) > 1:
            data = value.pop()
            # print("Process : {} ".format(data))
            if data.find("-999") == -1:
                return data
            else:
                print("Missing Serial Data")
                return "-1"
        else:
            print("NO DATA")
            return "-1"


@app.route('/process2', methods=['POST'])
def process2():
    # print("Process 2")
    data = ""
    global buffer
    data += buffer
    # print("Buffer : " + buffer)
    for state in actuator_state.values():
        data += "," + str(state)
    if data == "":
        return "-1"
    # print(data)
    return data


@app.route('/update_parameters', methods=['POST'])
def update_parameters():
    data_csv = request.form["value"]
    print("Update Parameters : {} ".format(data_csv))
    global buffer
    buffer = data_csv
    # t2 = threading.Thread(target=file_write, args=(file_name, buffer))
    # t2.start()
    file = open(file_name, "w")
    file.write(buffer)
    file.close()
    return "1"


@app.route('/nextpage')
def nextpage():
    return render_template('form2.html')


@app.route('/manual', methods=['POST'])
def manual():
    state = request.form['state']
    actuator_state['manual'] = str2bool(state)
    # print("Manual Control Activation : {} ".format(state))
    return "1"


@app.route('/exhaust', methods=['POST'])
def exhaust():
    state = request.form['state']
    actuator_state['exhaust'] = str2bool(state)
    print("Exhaust : {}".format(actuator_state))
    alter_pin(EXHAUST, str2bool(state))
    return "1"


@app.route('/waterp', methods=['POST'])
def waterp():
    state = request.form['state']
    actuator_state['waterp'] = str2bool(state)
    print("Water Pump : {}".format(actuator_state))
    alter_pin(WATERP, str2bool(state))
    return "1"


@app.route('/light', methods=['POST'])
def light():
    state = request.form['state']
    actuator_state['light'] = str2bool(state)
    print("Light : {}".format(actuator_state))
    alter_pin(LED, str2bool(state))
    return "1"


@app.route('/peltier', methods=['POST'])
def peltier():
    state = request.form['state']
    actuator_state['peltier'] = str2bool(state)
    print("Peltier : {}".format(actuator_state))
    alter_pin(PELTIER_FAN, str2bool(state))
    alter_pin(PELTIER, str2bool(state))
    return "1"


def alter_pin(pin, state):
    # print("Turn pin {} to {}".format(pin, state))
    if state:
        GPIO.output(pin, GPIO.LOW)
    else:
        GPIO.output(pin, GPIO.HIGH)


# def file_write(file_name, buffer):
#     print("in thread file_write")
#     file = open(file_name, "w")
#     file.write(buffer)
#     file.close()
#     return


def serial_input():
    ser = serial.Serial(PORT, 9600)
    while True:
        data = (ser.readline()).decode('UTF-8')
        global flag
        flag = 1
        value.append(data)
        flag = 0
        # print("Serial Input : {} ".format(data))
        auto_check(data)
        time.sleep(1)


def auto_check(data):
    # print("Auto_check : {} ".format(data))
    if len(data.split(",")) < 5:
        print("Error in DATA received")
        return
    # print("Auto_check : {} ".format(buffer))
    sensor_values = [float(i) for i in data.strip().split(",")]
    if actuator_state['manual']:
        return
    else:
        automation(sensor_values)


def automation(sensor_values):
    global buffer
    optimal_values = [float(i) for i in buffer.strip().split(",")]
    # print("is {} less than {} ".format(sensor_values[2], optimal_values[2]))
    alter_pin(LED, sensor_values[2] < optimal_values[2])
    alter_pin(EXHAUST, sensor_values[0] > optimal_values[0])
    alter_pin(PELTIER_FAN, sensor_values[0] < optimal_values[0])
    alter_pin(PELTIER, sensor_values[0] < optimal_values[0])
    alter_pin(WATERP, sensor_values[4] < optimal_values[4])


def str2bool(v):
    return v == "true"


t1 = threading.Thread(target=serial_input)
t1.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0')