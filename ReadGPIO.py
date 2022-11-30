from pidev.Cyprus_Commands import Cyprus_Commands_RPi as cyprus
import math
import sys
import time

from time import sleep
from datetime import datetime
from threading import Thread
import odrive
import os
import RPi.GPIO as GPIO
from pidev.stepper import stepper

od = odrive.find_any()

import sys
from binascii import hexlify

import pygatt

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

from odrive_helpers import *
import time




od_1 = find_odrive(serial_number="208D3388304B")
od_2 = find_odrive(serial_number="20553591524B")


assert od_1.config.enable_brake_resistor is True, "Check for faulty brake resistor."
assert od_2.config.enable_brake_resistor is True, "Check for faulty brake resistor."


print("yo")


horse1 = ODriveAxis(od_2.axis0, current_lim=10, vel_lim=10)
horse2 = ODriveAxis(od_2.axis1, current_lim=10, vel_lim=10)
horse3 = ODriveAxis(od_1.axis0, current_lim=10, vel_lim=10)
horse4 = ODriveAxis(od_1.axis1, current_lim=10, vel_lim=10)

horse1.set_gains()
horse2.set_gains()
horse3.set_gains()
horse4.set_gains()


horses = [horse1, horse2, horse3, horse4]
for horse in horses:
    horse.set_ramped_vel(1, 1)
sleep(3)
for horse in horses:
    horse.wait_for_motor_to_stop()  # waiting until motor slowly hits wall

for horse in horses:
    horse.set_vel(0)

print("nuts")
for i in range(10000):

    print(horse1.get_pos())
    digital_read(od_1, 2)
    sleep(1)



    time.sleep(0.1)

print("done")

