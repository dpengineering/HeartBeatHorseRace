import os
import sys
import pygatt
import kivy
from binascii import hexlify
from ObjectOrientedTest import *
from Player import *

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'egl_rpi'

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

import time

s.open_server()
print('waiting for connection')
s.wait_for_connection()


def heartrate_baseline(player_num):
    def handle_data(handle, value):
        global i
        heartrate = int(hexlify(value)[2:4], 16)

        byteHeartrate1 = bytes(str(heartrate), 'utf-8')
        byteHeartrate2 = bytes(str(heartrate), 'utf-8')
        byteHeartrate3 = bytes(str(heartrate), 'utf-8')
        byteHeartrate4 = bytes(str(heartrate), 'utf-8')


        if heartrate_is_real(heartrate):
            if player_num == 1:
                s.send_packet(PacketType.COMMAND1, byteHeartrate1)
            elif player_num == 2:
                s.send_packet(PacketType.COMMAND1, byteHeartrate2)
            elif player_num == 3:
                s.send_packet(PacketType.COMMAND1, byteHeartrate3)
            elif player_num == 4:
                s.send_packet(PacketType.COMMAND1, byteHeartrate4)
            else:
                print('not good')
        else:
            print('unlucky')
            i -= 1

    return handle_data

adapter1.start()
print('adapter1 started')

vernier1 = adapter1.connect(player1.deviceID, address_type=pygatt.BLEAddressType.random)

try:
    vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(1))


    while True:
        time.sleep(10)
        print("while True is running")
        s.close_server()
        break


finally:
    adapter1.stop()
    s.close_connection()
    s.close_server()

