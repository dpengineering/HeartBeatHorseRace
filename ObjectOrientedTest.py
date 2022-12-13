import sys
from binascii import hexlify
from Player import Player
import horserace_helpers

import pygatt

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

from odrive_helpers import *
from time import *

od_1 = find_odrive(serial_number="208D3388304B")
od_2 = find_odrive(serial_number="20553591524B")

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

p1 = Player("C6:4B:DF:A5:36:0B", od_2, 1, horse1, 60)
p2 = Player("A0:9E:1A:49:A8:51", od_2, 2, horse2, 60)
p3 = Player("A0:9E:1A:5E:EF:F6", od_1, 3, horse3, 60)
p4 = Player("", od_1, 4, horse4, 60)

horses = [horse1, horse2, horse3, horse4]

horserace_helpers.horse_setup(horses)

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

    def end_game(player_num):
        print("Player " + str(player_num) + " Wins!")

        # vernier1.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier2.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier3.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier4.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")

        adapter1.stop()
        adapter2.stop()
        # adapter3.stop()

        horse1.set_vel(0)
        horse2.set_vel(0)
        horse3.set_vel(0)
        horse4.set_vel(0)

        horse1.idle()
        horse2.idle()
        horse3.idle()
        horse4.idle()


def setup(player_num):
    total_laps = horserace_helpers.total_laps

    def handle_data(self, value):
        if player_num == 1:
            p1.handle_tick(value)
            if p1.get_laps() >= total_laps:
                end_game(1)
        elif player_num == 2:
            p2.handle_tick(value)
            if p2.get_laps() >= total_laps:
                end_game(2)
        elif player_num == 3:
            p3.handle_tick(value)
            if p3.get_laps() >= total_laps:
                end_game(3)
        else:
            p4.handle_tick(value)
            if p4.get_laps() >= total_laps:
                end_game(4)

    def end_game(num):
        print("Player " + str(num) + " Wins!")

        # vernier1.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier2.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier3.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier4.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        p1.game_done()
        p2.game_done()
        p3.game_done()
        p4.game_done()

        adapter1.stop()
        adapter2.stop()
        # adapter3.stop()

        horse1.set_vel(0)
        horse2.set_vel(0)
        horse3.set_vel(0)
        horse4.set_vel(0)

        horse1.idle()
        horse2.idle()
        horse3.idle()
        horse4.idle()

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
    chest_polar2 = adapter2.connect("A0:9E:1A:5E:EF:F6")

    chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(
        1))  # subscribing to heart rate measurement with the long letter-number ; when this line recieves new data, the callback function runs
    hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(2))
    chest_polar2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(3))



    # The subscription runs on a background thread. You must stop this main
    # thread from exiting, otherwise you will not receive any messages, and
    # the program will exit. Sleeping in a while loop like this is a simple
    # solution that won't eat up unnecessary CPU, but there are many other
    # ways to handle this in more complicated program. Multi-threaded
    # programming is outside the scope of this README.

    p1.start_game()
    p2.start_game()
    p3.start_game()

    while True:
        sleep(10)
        print("while True is running")
finally:
    adapter0.stop()
    adapter1.stop()
    adapter2.stop()
