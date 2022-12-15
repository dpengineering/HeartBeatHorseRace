#testing code, no longer useful

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
        base_velo = 0.5  # will get this from something else later
        heart_weight = 70  # will set at some point

        print("Heart rate is " + str(int(hexlify(value)[2:4], 16)))
        data = int(hexlify(value)[2:4], 16)

        if -2 < ((base_velo + ((data - baseline1) / heart_weight)) * -1) < 0:
            velocity1 = ((base_velo + ((data - baseline1) / heart_weight)) * -1)
        else:
            velocity1 = 0
            print('1 positive velocity')
        if -2 < ((base_velo + ((data - baseline2) / heart_weight)) * -1) < 0:
            velocity2 = ((base_velo + ((data - baseline2) / heart_weight)) * -1)
        else:
            velocity2 = 0
            print('2 positive velocity')
        if -2 < ((base_velo + ((data - baseline3) / heart_weight)) * -1) < 0:
            velocity3 = ((base_velo + ((data - baseline3) / heart_weight)) * -1)
        else:
            velocity3 = 0
            print('3 positive velocity')
        if -2 < ((base_velo + ((data - baseline4) / heart_weight)) * -1) < 0:
            velocity4 = ((base_velo + ((data - baseline4) / heart_weight)) * -1)
        else:
            velocity4 = 0
            print('3 positive velocity')

        print("Player 1's velocity is " + str(velocity1))
        print("Player 2's velocity is " + str(velocity2))
        print("Player 3's velocity is " + str(velocity3))
        print("Player 4's velocity is " + str(velocity4))

        if player_num == 1:
            horse1.set_vel(velocity1)
        elif player_num == 2:
            horse2.set_vel(velocity2)
        elif player_num == 3:
            horse3.set_vel(velocity3)
        else:
            horse4.set_vel(velocity4)

    print("hello?")

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
