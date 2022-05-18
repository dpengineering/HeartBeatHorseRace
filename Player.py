import pygatt
from binascii import hexlify
from time import sleep
from odrive_helpers import *


class Player:

    deviceMap = {
        "49A85121": "A0:9E:1A:49:A8:51",
        "5EEFF62F": "A0:9E:1A:5E:EF:F6",
        "A3DDF820": "C6:4B:DF:A5:36:0B",
        "9F43FF2B": "F8:FF:5C:77:2A:A1",
        "A3DDDD2F": "EF:FD:6F:EE:D7:81" #horse 1
    }

    def __init__(self, deviceID, od, axis):
        self.deviceID = deviceID
        self.od = od
        self.axis = axis

    def heart_rate_average(self, lst):
        return sum(lst) / len(lst)

    def handle_data_for_axis(self, count, lst):
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
                average = self.heart_rate_average(lst)
                print("Average Value: ", average)
                #print("Delta: ", rate - average)
                maxSpeed = average + 50
                speed = ((10*((Crate-average)/(maxSpeed-average))) + 1)/10

                accel = 2

                if 1/10 < speed < 11/10:
                    speed = speed
                    self.axis.set_ramped_vel(-speed, accel)

                if speed < 1/10:
                    speed = 1/10
                    self.axis.set_ramped_vel(-speed, accel)

                if speed > 11/10:
                    speed = 11/10
                    self.axis.set_ramped_vel(-speed, accel)

                print("Speed: ", speed)

        return handle_data

if __name__ == "__main__":
    od_2 = find_odrive(serial_number="20553591524B")
    horse1 = ODriveAxis(od_2.axis0, current_lim=10, vel_lim=10)
    adapter0 = pygatt.BGAPIBackend()
    player = Player("EF:FD:6F:EE:D7:81", od_2, horse1)

    try:
        adapter0.start()
        #adapter1.start()

        # These two adapters are connecting to H7 Polar devices
        # chest_polar = adapter0.connect("A0:9E:1A:49:A8:51")
        hand_polar = adapter0.connect(player.deviceID, address_type=pygatt.BLEAddressType.random)

        # USE THIS FOR CONNECTING TO THE NEWER H9 POLAR
        # H9_Polar = adapter.connect("F8:FF:5C:77:2A:A1", address_type=pygatt.BLEAddressType.random)

        # chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(0))

        # ax.set_vel(5)
        dump_errors(od_2)

        hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=player.handle_data_for_axis(0, []))

        #hand_polar1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_axis(ax1, 0, []))        # The subscription runs on a background thread. You must stop this main
        # thread from exiting, otherwise you will not receive any messages, and
        # the program will exit. Sleeping in a while loop like this is a simple
        # solution that won't eat up unnecessary CPU, but there are many other
        # ways to handle this in more complicated program. Multi-threaded
        # programming is outside the scope of this README.
        while True:
            sleep(1)
    finally:
        adapter0.stop()
        horse1.set_vel(0)
        horse1.idle()
        # adapter1.stop()

