from __future__ import print_function

# python imports
from multiprocessing import Process, Value, Array, Queue
from collections import deque
from time import sleep

# RPi imports
import serial

# my imports
from capture_layer import CaptureLayer
from input_layer import InputLayer
from control_layer import ControlLayer

motor_busy = Value('b')
motor_busy.value = True
control_vector = Array('f', [0,0,0])


def serial_control():
    global motor_busy, control_vector

    port = serial.Serial(port='/dev/ttyS0', baudrate = 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS,timeout=.01)

    while 1:
        s_in = port.readline()
        if len(s_in) > 0:
            motor_busy.value = 1 if (s_in[:4] == "busy") else 0
            #print(motor_busy.value, s_in)

        port.write("X%d \n" % control_vector[0])

        if control_vector[1] != 0:
            data = "C%d \n" % control_vector[1]
            port.write(data)
            print("sent data:", data)

        port.write("S%f \n" % control_vector[2])

########################################################
def main():

    capture_layer = CaptureLayer()
    input_layer = InputLayer()
    control_layer = ControlLayer()

    main_loop = True

    capture_thread = Process(target=capture_layer.run_capture)
    serial_thread = Process(target=serial_control)

    capture_thread.start()
    serial_thread.start()
    last_busy = 1

    while main_loop:
        shape = capture_layer.marker_shape[:]

        input_layer.update(shape, motor_busy.value)

        control_layer.update(input_layer)
        control_vector[0:3] = control_layer.get_control_vector()

        if last_busy != motor_busy.value:
            last_busy = motor_busy.value
            print("BUSY" if motor_busy.value else "FREE")

        if control_vector[1] != 0:
            print("%d cm, %.1f deg" % (input_layer.distance_cm, input_layer.angle_deg)," "*8)
            print("desired %d cm = %d steps" % (control_layer.desired_cm, control_vector[1]),
                "conf: %.2f" % input_layer.distance_filter.confidence())

        sleep(0.020)

########################################################
if __name__ == '__main__':
    main()