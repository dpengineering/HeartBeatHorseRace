# This file defines several functions and variables called from main.py
import sys
from binascii import hexlify
from Player import Player
import horserace_helpers
from kivy.uix.screenmanager import ScreenManager

import pygatt

from odrive_helpers import *
import time
import enum

sys.path.append("/home/pi/HeartBeatHorseRace/")

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
baseline1 = 60
baseline2 = 60
baseline3 = 60
baseline4 = 60

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

homed = False
serverCreated = False
print(homed)
i = 0
total_laps = 3

player1 = Player("C6:4B:DF:A5:36:0B", od_2, 1, horse1, baseline1, 0)
player2 = Player("A0:9E:1A:49:A8:51", od_2, 2, horse2, baseline2, 0)
player3 = Player("A0:9E:1A:5E:EF:F6", od_1, 3, horse3, baseline3, 0)
player4 = Player("DF:CF:39:84:C2:78", od_1, 4, horse4, baseline4, 0)

byteHeartrate = 0
heartrate = 0
laps = 0


class PacketType(enum.Enum):
    COMMAND0 = 0
    COMMAND1 = 1
    COMMAND2 = 2
    COMMAND3 = 3

s = Server("172.17.21.3", 5001, PacketType)


def heartrate_is_real(heartrate):
    if (heartrate > 30):
        if (heartrate < 170):
            return True
    else:
        return False


def heartrate_baseline(player_num):
    def handle_data(handle, value):
        global i, byteHeartrate, heartrate, laps
        heartrate = int(hexlify(value)[2:4], 16)
        byteHeartrate = bytes(str(heartrate), 'utf-8')

        if heartrate_is_real(heartrate):
            if player_num == 1:
                baseline1List.append(heartrate)
                msg = str(heartrate) + "-" + str(laps)
                byteMsg = bytes(str(msg), 'utf-8')
                if serverCreated is True:
                    s.send_packet(PacketType.COMMAND0, byteMsg)
            elif player_num == 2:
                baseline2List.append(heartrate)
                msg = str(heartrate) + "-" + str(laps)
                byteMsg = bytes(str(msg), 'utf-8')
                if serverCreated is True:
                    s.send_packet(PacketType.COMMAND1, byteMsg)
            elif player_num == 3:
                baseline3List.append(heartrate)
                msg = str(heartrate) + "-" + str(laps)
                byteMsg = bytes(str(msg), 'utf-8')
                if serverCreated is True:
                    s.send_packet(PacketType.COMMAND2, byteMsg)
            elif player_num == 4:
                baseline4List.append(heartrate)
                msg = str(heartrate) + "-" + str(laps)
                byteMsg = bytes(str(msg), 'utf-8')
                if serverCreated is True:
                    s.send_packet(PacketType.COMMAND3, byteMsg)
            else:
                print('not good')
        else:
            print('unlucky')

        return byteHeartrate

    return handle_data


def create_server():
    global serverCreated
    print('server created')
    s.open_server()
    print('server opened, now waiting for connection!')
    s.wait_for_connection()
    serverCreated = True
    return True


def average_heartrate(lst):
    if not len(lst) == 0:
        if not sum(lst) == 0:
            return sum(lst) / len(lst)
        else:
            return 'not averaged'

def go_home():
    horse1.get_home()
    horse2.get_home()
    horse3.get_home()
    horse4.get_home()


def setup(player_num):
    global byteHeartrate, heartrate
    total_laps = horserace_helpers.total_laps

    def handle_data(self, value):
        global laps
        if player_num == 1:
            laps = player1.get_laps()
            msg = str(heartrate) + "-" + str(laps)
            byteMsg = bytes(str(msg), 'utf-8')
            player1.handle_tick(value)
            if serverCreated is True:
                s.send_packet(PacketType.COMMAND0, byteMsg)
            # if laps >= total_laps:
            #     end_game(1)
        elif player_num == 2:
            laps = player1.get_laps()
            msg = str(heartrate) + "-" + str(laps)
            byteMsg = bytes(str(msg), 'utf-8')
            player2.handle_tick(value)
            if serverCreated is True:
                s.send_packet(PacketType.COMMAND1, byteMsg)
            # if player2.get_laps() >= total_laps:
            #     end_game(2)
        elif player_num == 3:
            laps = player1.get_laps()
            msg = str(heartrate) + "-" + str(laps)
            byteMsg = bytes(str(msg), 'utf-8')
            player3.handle_tick(value)
            if serverCreated is True:
                s.send_packet(PacketType.COMMAND2, byteMsg)
            # if player3.get_laps() >= total_laps:
            #     end_game(3)
        else:
            laps = player1.get_laps()
            msg = str(heartrate) + "-" + str(laps)
            byteMsg = bytes(str(msg), 'utf-8')
            player4.handle_tick(value)
            if serverCreated is True:
                s.send_packet(PacketType.COMMAND3, byteMsg)
            # if player4.get_laps() >= total_laps:
            #     end_game(4)
    # def end_game(num):
    #     print("Player " + str(num) + " Wins!")
    #     if serverCreated is True:
    #         if num == 1:
    #             s.send_packet(PacketType.COMMAND0, b'WIN')
    #             print('yeet')
    #         elif num == 2:
    #             s.send_packet(PacketType.COMMAND1, b'WIN')
    #         elif num == 3:
    #             s.send_packet(PacketType.COMMAND2, b'WIN')
    #         else:
    #             s.send_packet(PacketType.COMMAND3, b'WIN')
    #     player1.is_done = True
    #     player2.is_done = True
    #     player3.is_done = True
    #     player4.is_done = True
    #     sleep(2)

    return handle_data

def home_all_horses():
    horses = [horse1, horse2, horse3, horse4]
    for horse in horses:
        horse.set_ramped_vel(2, 2)
    sleep(1)
    for horse in horses:
        horse.wait_for_motor_to_stop()  # waiting until motor slowly hits wall
    for horse in horses:
        horse.set_pos_traj(horse.get_pos() - 0.5, 1, 2, 1)
    sleep(3)  # allows motor to start moving to offset position
    for horse in horses:
        horse.wait_for_motor_to_stop()
    for horse in horses:
        if round(horse.get_pos()) != 0:
            horse.set_ramped_vel(1, 1)
            sleep(1)
            horse.wait_for_motor_to_stop()
            horse.set_pos_traj(horse.get_pos() - 0.5, 1, 2, 1)
            sleep(3)
            horse.wait_for_motor_to_stop()