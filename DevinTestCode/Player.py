import pygatt
from binascii import hexlify
import time
from time import sleep
from ODrive_Ease_Lib import *


class Player:

    deviceMap = {
        "49A85121": "A0:9E:1A:49:A8:51",
        "5EEFF62F": "A0:9E:1A:5E:EF:F6",
        "A3DDF820": "C6:4B:DF:A5:36:0B",
        "9F43FF2B": "F8:FF:5C:77:2A:A1",
        "A3DDDD2F": "EF:FD:6F:EE:D7:81"
    }

    def __init__(self, deviceID, od, axis):
        self.deviceID = deviceID
        self.od = od
        self.axis = axis

    def handle_data_for_axis(self, axG, count, lst):
        def handle_data(handle, value):
            """
            handle -- integer, characteristic read handle the data was received on
            value -- bytearray, the data returned in the notification
            """

            nonlocal count
            nonlocal lst
            #dump_err2000/a + a + 33ors(od)
            #print("Received data: %s" % hexlify(value))
            print("Player 1 Heart Rate: %s" % (int(hexlify(value)[2:4], 16)))
            if count < 10:
                if (int(hexlify(value)[2:4], 16)) != 0 and 40 < (int(hexlify(value)[2:4], 16)) < 150:
                    lst.append((int(hexlify(value)[2:4], 16)))
                    count += 1
            else:
                Crate = int(hexlify(value)[2:4], 16)
                average = Average(lst)
                print("Average Value: ", average)
                #print("Delta: ", rate - average)
                maxSpeed = average + 50
                speed = (10*((Crate-average)/(maxSpeed-average))) + 1

                accel = 2

                if 1 < speed < 11:
                    speed = speed
                    axG.set_ramped_vel(speed, accel)

                if speed < 1:
                    speed = 1
                    axG.set_ramped_vel(1, accel)

                if speed > 11:
                    speed = 11
                    axG.set_ramped_vel(11, accel)

                print("Speed: ", speed)


