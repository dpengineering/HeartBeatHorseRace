import pygatt
from binascii import hexlify
from time import sleep
from odrive_helpers import *
from threading import Thread

total_laps = 3
steadymove_baseline = 40

def horse_setup(horses):

    for horse in horses:
        horse.set_gains()

    for horse in horses:
        if not horse.is_calibrated():
            print("calibrating horse...")
            horse.calibrate_with_current_lim(15)

    for horse in horses:
        horse.set_ramped_vel(1, 1)
    sleep(3)
    for horse in horses:
        horse.wait_for_motor_to_stop()  # waiting until motor slowly hits wall
    for horse in horses:
        horse.set_pos_traj(horse.get_pos() - 0.5, 1, 2, 1)
    sleep(3)  # allows motor to start moving to offset position
    for horse in horses:
        horse.wait_for_motor_to_stop()
    for horse in horses:
        horse.set_home()

    for horse in horses:
        print("Current Limit Horse1: ", horse.get_current_limit())
        print("Velocity Limit Horse1: ", horse.get_vel_limit())

    for horse in horses:
        horse.set_vel(0)

