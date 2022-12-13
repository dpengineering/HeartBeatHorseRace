import sys
from binascii import hexlify
from Player import Player
import horserace_helpers
from kivy.uix.screenmanager import ScreenManager

import pygatt

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

from odrive_helpers import *
import time

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

SCREEN_MANAGER = ScreenManager()
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

numberOfPlayers = 0
baseline1 = 0
baseline2 = 0
baseline3 = 0
baseline4 = 0

h1_laps = 0
h2_laps = 0
h3_laps = 0
h4_laps = 0

h1_timer = time.time()
h2_timer = time.time()
h3_timer = time.time()
h4_timer = time.time()

baseline1List = []
baseline2List = []
baseline3List = []
baseline4List = []

homed = 0
i = 0
total_laps = 3

player1 = Player("C6:4B:DF:A5:36:0B", od_2, 1, horse1, baseline1)
player2 = Player("A0:9E:1A:49:A8:51", od_2, 2, horse2, baseline2)
player3 = Player("A0:9E:1A:5E:EF:F6", od_1, 3, horse3, baseline3)
player4 = Player("", od_1, 4, horse4, baseline4)

new_game = False


def heartrate_is_real(heartrate):
    if (heartrate > 30):
        if (heartrate < 170):
            return True
    else:
        return False

    def end_game(player_num):
        global new_game
        print("Player " + str(player_num) + " Wins!")

        # vernier1.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier2.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier3.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier4.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")

        horse1.get_home()
        horse2.get_home()
        horse3.get_home()
        horse4.get_home()

        print('horses home')
        new_game = True
        print('new game is true')
        return new_game


def heartrate_baseline(player_num):
    def handle_data(handle, value):
        global i
        heartrate = int(hexlify(value)[2:4], 16)

        if heartrate_is_real(heartrate):
            if player_num == 1:
                baseline1List.append(heartrate)
            elif player_num == 2:
                baseline2List.append(heartrate)
            elif player_num == 3:
                baseline3List.append(heartrate)
            elif player_num == 4:
                baseline4List.append(heartrate)
            else:
                print('not good')
        else:
            print('unlucky')
            i -= 1

    return handle_data


def average_heartrate(lst):
    if not len(lst) == 0:
        return sum(lst) / len(lst)
    else:
        return 'not averaged'


def setup(player_num):
    total_laps = horserace_helpers.total_laps

    def handle_data(self, value):
        if player_num == 1:
            player1.handle_tick(value)
            if player1.get_laps() >= total_laps:
                end_game(1)
        elif player_num == 2:
            player2.handle_tick(value)
            if player2.get_laps() >= total_laps:
                end_game(2)
        elif player_num == 3:
            player3.handle_tick(value)
            if player3.get_laps() >= total_laps:
                end_game(3)
        else:
            player4.handle_tick(value)
            if player4.get_laps() >= total_laps:
                end_game(4)

    def end_game(num):
        print("Player " + str(num) + " Wins!")

        # vernier1.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier2.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier3.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        # vernier4.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        player1.game_done()
        player2.game_done()
        player3.game_done()
        player4.game_done()

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


# try:
#     adapter1.start()
#     print("adapter0 started")
#     adapter2.start()
#     print("adapter1 started")
#     adapter3.start()
#     print("adapter2 started")
#
#     # These two adapters are connecting to H7 Polar devices
#     # DO NOT SPECIFY AN ADDRESS TYPE AS RANDOM FOR H7 POLARS
#
#     # Each address can be found in the HeartRateExample DPEA repo
#     chest_polar = adapter1.connect("C6:4B:DF:A5:36:0B", address_type=pygatt.BLEAddressType.random)
#     hand_polar = adapter2.connect("A0:9E:1A:49:A8:51")
#     chest_polar2 = adapter3.connect("A0:9E:1A:5E:EF:F6")
#
#     chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(
#         1))  # subscribing to heart rate measurement with the long letter-number ; when this line recieves new data, the callback function runs
#     hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(2))
#     chest_polar2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(3))
#
#
#
#     # The subscription runs on a background thread. You must stop this main
#     # thread from exiting, otherwise you will not receive any messages, and
#     # the program will exit. Sleeping in a while loop like this is a simple
#     # solution that won't eat up unnecessary CPU, but there are many other
#     # ways to handle this in more complicated program. Multi-threaded
#     # programming is outside the scope of this README.
#
#     player1.start_game()
#     player2.start_game()
#     player3.start_game()
#
#     while True:
#         sleep(10)
#         print("while True is running")
# finally:
#     adapter1.stop()
#     adapter2.stop()
#     adapter3.stop()
