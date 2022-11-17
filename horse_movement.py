import sys
from binascii import hexlify

import pygatt

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

from odrive_helpers import *
import time




od_1 = find_odrive(serial_number="208D3388304B")
od_2 = find_odrive(serial_number="20553591524B")

digital_read(od_1, 8)
digital_read(od_1, 2)
digital_read(od_2, 8)
digital_read(od_2, 2)

assert od_1.config.enable_brake_resistor is True, "Check for faulty brake resistor."
assert od_2.config.enable_brake_resistor is True, "Check for faulty brake resistor."

#

# Each adapter finds a Bluetooth Serial Port connected to the Raspberry Pi

adapter0 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM2')
adapter1 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM3')
adapter2 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM4')

horse1 = ODriveAxis(od_2.axis0, current_lim=10, vel_lim=10)
horse2 = ODriveAxis(od_2.axis1, current_lim=10, vel_lim=10)
horse3 = ODriveAxis(od_1.axis0, current_lim=10, vel_lim=10)
horse4 = ODriveAxis(od_1.axis1, current_lim=10, vel_lim=10)

horse1.set_gains()
horse2.set_gains()
horse3.set_gains()
horse4.set_gains()



if not horse1.is_calibrated():
    print("calibrating horse1...")
    horse1.calibrate_with_current_lim(15)
if not horse2.is_calibrated():
    print("calibrating horse2...")
    horse2.calibrate_with_current_lim(15)
if not horse3.is_calibrated():
    print("calibrating horse3...")
    horse3.calibrate_with_current_lim(15)
if not horse4.is_calibrated():
    print("calibrating horse4...")
    horse4.calibrate_with_current_lim(15)


horses = [horse1, horse2, horse3, horse4]
for horse in horses:
    horse.set_ramped_vel(1, 1)
sleep(2)
for horse in horses:
    horse.wait_for_motor_to_stop()  # waiting until motor slowly hits wall
for horse in horses:
    horse.set_pos_traj(horse.get_pos() - 0.5, 1, 2, 1)
sleep(3)  # allows motor to start moving to offset position
for horse in horses:
    horse.wait_for_motor_to_stop()
for horse in horses:
    horse.set_home()


print("Current Limit Horse1: ", horse1.get_current_limit())
print("Velocity Limit Horse1: ", horse1.get_vel_limit())
print("Current Limit Horse2: ", horse2.get_current_limit())
print("Velocity Limit Horse2: ", horse2.get_vel_limit())
print("Current Limit Horse3: ", horse3.get_current_limit())
print("Velocity Limit Horse3: ", horse3.get_vel_limit())
print("Current Limit Horse4: ", horse4.get_current_limit())
print("Velocity Limit Horse4: ", horse4.get_vel_limit())

horse1.set_vel(0)
horse2.set_vel(0)
horse3.set_vel(0)
horse4.set_vel(0)

dump_errors(od_1)
dump_errors(od_2)

od_1.clear_errors()
od_2.clear_errors()

od_1.axis0.controller.config.enable_overspeed_error = False
od_1.axis1.controller.config.enable_overspeed_error = False
od_2.axis0.controller.config.enable_overspeed_error = False
od_2.axis1.controller.config.enable_overspeed_error = False


def heartrate_is_real(heartrate):

    if (heartrate > 30):
        if (heartrate < 170):
            return True
    else:
        return False


def velocity_movement(player_num):
    def handle_data(handle, value):
        base_velo = 0.3  # will get this from something else later
        heart_weight = 30  # will set at some point
        baseline_rate = 60 # get from something else as well

        print("Heart rate is " + str(int(hexlify(value)[2:4], 16)))
        data = int(hexlify(value)[2:4], 16)
        t = (data - baseline_rate) / heart_weight

        if not heartrate_is_real(data):
            return None

        velocity = (base_velo + t)  * -1
        print(t)
        print("Player " + str(player_num) + "'s velocity is " + str(velocity))

        if player_num == 1:
            horse1.set_vel(velocity)
        elif player_num == 2:
            horse2.set_vel(velocity)
        elif player_num == 3:
            horse3.set_vel(velocity)
        else:
            horse4.set_vel(velocity)

    return handle_data


def position_movement(player_num):
    def handle_data(handle, value):
        heart_weight = 20  # will set at some point
        baseline_rate = 60  # get from something else as well

        print("Heart rate is " + str(int(hexlify(value)[2:4], 16)))
        t = (int(hexlify(value)[2:4], 16) - baseline_rate) / heart_weight

        if not heartrate_is_real(t):
            return

        if player_num == 1:
            horse = horse1
        elif player_num == 2:
            horse = horse2
        elif player_num == 3:
            horse = horse3
        else:
            horse = horse4

        horse.set_pos(horse.get_pos + t)

        print("Player " + str(player_num) + " will move" + str(t) + " rotations")

        return handle_data


try:
    adapter0.start()
    print("adapter0 started")
    adapter1.start()
    print("adapter1 started")
    adapter2.start()
    print("adapter2 started")

    # These two adapters are connecting to H7 Polar devices
    # DO NOT SPECIFY AN ADDRESS TYPE AS RANDOM FOR H7 POLARS

    # Each address can be found in the HeartRateExample DPEA repo
    chest_polar = adapter0.connect("C6:4B:DF:A5:36:0B", address_type=pygatt.BLEAddressType.random)
    hand_polar = adapter1.connect("A0:9E:1A:49:A8:51")
    #chest_polar2 = adapter2.connect("A0:9E:1A:49:A8:51")

    chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=velocity_movement(1))  # subscribing to heart rate measurement with the long letter-number ; when this line recieves new data, the callback function runs
    hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=velocity_movement(2))
    #chest_polar2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=velocity_movement(3))

    # The subscription runs on a background thread. You must stop this main
    # thread from exiting, otherwise you will not receive any messages, and
    # the program will exit. Sleeping in a while loop like this is a simple
    # solution that won't eat up unnecessary CPU, but there are many other
    # ways to handle this in more complicated program. Multi-threaded
    # programming is outside the scope of this README.

    while True:
        time.sleep(10)
        print("while True is running")
finally:
    adapter0.stop()
    adapter1.stop()
    adapter2.stop()
