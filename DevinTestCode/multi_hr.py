import pygatt
from binascii import hexlify
import time
from time import sleep
from ODrive_Ease_Lib import *
from Player import *

adapter0 = pygatt.BGAPIBackend(serial_port="/dev/ttyACM2")
adapter1 = pygatt.BGAPIBackend(serial_port="/dev/ttyACM1")
#adapter1 = pygatt.GATTToolBackend()


od = find_odrive()
ax = ODrive_Axis(od.axis0)
ax1 = ODrive_Axis(od.axis1)
# Basic motor tuning, for more precise tuning follow this guide: https://docs.odriverobotics.com/control.html#tuning
ax.set_gains()
ax1.set_gains()

if not ax.is_calibrated():
    print("calibrating 0...")
    # ax.calibrate()
    ax.calibrate_with_current_lim(30)
ax.set_vel(1)

sleep(5)

if not ax1.is_calibrated():
    print("calibrating 1...")
    # ax.calibrate()
    ax1.calibrate_with_current_lim(30)
ax1.set_vel(1)


def handle_data_for_axis(axG, count, lst):
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

def handle_data1(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    global count1
    global lst1
    #dump_err2000/a + a + 33ors(od)
    #print("Received data: %s" % hexlify(value))
    print("Player 2 Heart Rate: %s" % (int(hexlify(value)[2:4], 16)))
    if count1 < 10:
        if (int(hexlify(value)[2:4], 16)) != 0 and 40 < (int(hexlify(value)[2:4], 16)) < 150:
            lst1.append((int(hexlify(value)[2:4], 16)))
            count1 += 1
    else:
        Crate = int(hexlify(value)[2:4], 16)
        average = Average(lst1)
        print("Average Value 1: ", average)
        #print("Delta: ", rate - average)
        maxSpeed = average + 50
        speed = (10*((Crate-average)/(maxSpeed-average))) + 1

        accel = 2

        if 1 < speed < 11:
            speed = speed
            ax1.set_ramped_vel(speed, accel)

        if speed < 1:
            speed = 1
            ax1.set_ramped_vel(1, accel)

        if speed > 11:
            speed = 11
            ax1.set_ramped_vel(11, accel)

        print("Speed 1: ", speed)



def Average(lst):
    return sum(lst) / len(lst)


try:
    adapter0.start()
    adapter1.start()
    
    #These two adapters are connecting to H7 Polar devices
    #chest_polar = adapter0.connect("A0:9E:1A:49:A8:51")
    hand_polar = adapter0.connect("F8:FF:5C:77:2A:A1", address_type=pygatt.BLEAddressType.random)
    hand_polar1 = adapter1.connect("EF:FD:6F:EE:D7:81", address_type=pygatt.BLEAddressType.random)


#USE THIS FOR CONNECTING TO THE NEWER H9 POLAR
    #H9_Polar = adapter.connect("F8:FF:5C:77:2A:A1", address_type=pygatt.BLEAddressType.random)

    #chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(0))



    #ax.set_vel(5)
    dump_errors(od)

    hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_axis(ax, 0, []))

    hand_polar1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_axis(ax1, 0, []))

    # The subscription runs on a background thread. You must stop this main
    # thread from exiting, otherwise you will not receive any messages, and
    # the program will exit. Sleeping in a while loop like this is a simple
    # solution that won't eat up unnecessary CPU, but there are many other
    # ways to handle this in more complicated program. Multi-threaded
    # programming is outside the scope of this README.
    while True:
        time.sleep(1)
finally:
    adapter0.stop()
    adapter1.stop()
    ax.set_vel(0)
    ax1.set_vel(0)
    ax.idle()
    ax1.idle()
    #adapter1.stop()
