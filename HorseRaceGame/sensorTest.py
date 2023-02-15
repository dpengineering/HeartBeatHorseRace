# This file defines several functions and variables called from main.py
import sys
from binascii import hexlify
from kivy.uix.screenmanager import ScreenManager

import pygatt

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

from odrive_helpers import *
import time
import enum
from p2p.dpea_p2p import Server

od_1 = find_odrive(serial_number="208D3388304B")
od_2 = find_odrive(serial_number="20553591524B")

assert od_1.config.enable_brake_resistor is True, "Check for faulty brake resistor."
assert od_2.config.enable_brake_resistor is True, "Check for faulty brake resistor."

horse1 = ODriveAxis(od_2.axis0, current_lim=10, vel_lim=10)
horse2 = ODriveAxis(od_2.axis1, current_lim=10, vel_lim=10)
horse3 = ODriveAxis(od_1.axis0, current_lim=10, vel_lim=10)
horse4 = ODriveAxis(od_1.axis1, current_lim=10, vel_lim=10)

adapter1 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM2')
adapter2 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM3')
adapter3 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM4')
adapter4 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM5')


MAIN_SCREEN_NAME = 'main'
TRAJ_SCREEN_NAME = 'traj'
GPIO_SCREEN_NAME = 'gpio'
ADMIN_SCREEN_NAME = 'admin'
BEGINNING_SCREEN_NAME = 'beginning'
BASELINE_SCREEN_NAME = 'baseline'
RUN_SCREEN_NAME = 'run'

od_1.axis0.controller.config.enable_overspeed_error = False
od_1.axis1.controller.config.enable_overspeed_error = False
od_2.axis0.controller.config.enable_overspeed_error = False
od_2.axis1.controller.config.enable_overspeed_error = False

while True:
    if digital_read(od_1, 8) == 0:
        print("seeing sensor")
    else:
        print("not seeing sensor")
