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


h1_laps = 0
h2_laps = 0
h3_laps = 0
h4_laps = 0

h1_timer = time.time()
h2_timer = time.time()
h3_timer = time.time()
h4_timer = time.time()


def setup(player_num):
    print("hello?")

    def end_game():
        print("Player " + str(player_num) + " Wins!")

        adapter0.stop()
        adapter1.stop()
        adapter2.stop()

        horse1.set_vel(0)
        horse2.set_vel(0)
        horse3.set_vel(0)
        horse4.set_vel(0)

    def track_laps():

        global h1_laps, h2_laps, h3_laps, h4_laps, h1_timer, h2_timer, h3_timer, h4_timer

        total_laps = 3

        buffer = 4

        if player_num == 1:
            if buffer < round((time.time() - h1_timer), 2):
                h1_laps += 1

                if h1_laps == total_laps:
                    end_game()

                h1_timer = time.time()
        elif player_num == 2:
            if buffer < round((time.time() - h2_timer), 2):
                h2_laps += 1

                if h2_laps == total_laps:
                    end_game()

                h2_timer = time.time()
        elif player_num == 3:
            if buffer < round((time.time() - h3_timer), 2):
                h3_laps += 1

                if h3_laps == total_laps:
                    end_game()

                h3_timer = time.time()
        else:
            if buffer < round((time.time() - h4_timer), 2):
                h4_laps += 1

                if h4_laps == total_laps:
                    end_game()

                h4_timer = time.time()

    def at_end():
        base_velo = -0.8
        if player_num == 1:
            track_laps()
            horse1.set_vel(2)
            horse1.wait_for_motor_to_stop()
            horse1.set_vel(-0.8)

        elif player_num == 2:
            track_laps()
            horse2.set_vel(2)
            horse2.wait_for_motor_to_stop()
            horse2.set_vel(-0.8)
        elif player_num == 3:
            track_laps()
            horse3.set_vel(2)
            horse3.wait_for_motor_to_stop()
            horse3.set_vel(-0.8)
        else:
            track_laps()
            horse4.set_vel(2)
            horse4.wait_for_motor_to_stop()
            horse4.set_vel(-0.8)
        return

    def velocity_movement(handle, value):
        base_velo = 0.8  # will get this from something else later
        heart_weight = 70  # will set at some point
        baseline_rate = 60  # get from something else as well

        print("Heart rate is " + str(int(hexlify(value)[2:4], 16)))
        data = int(hexlify(value)[2:4], 16)
        t = (data - baseline_rate) / heart_weight

        velocity = (base_velo + t) * -1

        if not heartrate_is_real(data):
            velocity = base_velo * -1

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

    def handle_tick(handle, value):

        if player_num == 1:
            horse = horse1
            time.sleep(0.5)
            if horse.get_vel() <= 0:
                if (digital_read(od_2, 2) == 0):

                    at_end()
                else:

                    velocity_movement(handle, value)
            else:
                return

        elif player_num == 2:
            horse = horse2

            if horse.get_vel() <= 0:
                if (digital_read(od_2, 8) == 0):

                    at_end()
                else:

                    velocity_movement(handle, value)
            else:
                return
        elif player_num == 3:
            horse = horse3

            if horse.get_vel() <= 0:
                if (digital_read(od_1, 2) == 0):

                    at_end()
                else:

                    velocity_movement(handle, value)
            else:
                return
        else:
            horse = horse4

            if horse.get_vel() <= 0:
                if (digital_read(od_1, 8) == 0):

                    at_end()
                else:

                    velocity_movement(handle, value)
            else:
                return

    horse1.set_vel(-0.5)
    horse2.set_vel(-0.5)
    # horse3.set_vel(-0.3)
    # horse4.set_vel(-0.3)

    return handle_tick


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
    # chest_polar2 = adapter2.connect("A0:9E:1A:5E:EF:F6")

    chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(
        1))  # subscribing to heart rate measurement with the long letter-number ; when this line recieves new data, the callback function runs
    hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(2))
    # chest_polar2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(3))

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
