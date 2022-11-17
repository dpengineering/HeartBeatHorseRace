import pygatt
from binascii import hexlify
import time

adapter0 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM2')
#adapter1 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM3')


def handle_data_for_player(player_num):
    def handle_data(handle, value):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """
        print(value)
        print("Received data: %s" % hexlify(value))
        print(" " * (32 * player_num) + "Player %s Heart Rate: %s" % (player_num, int(hexlify(value)[2:4], 16)))
        print(int(hexlify(value)[2:4], 16))

    return handle_data


try:
    adapter0.start()
    #adapter1.start()

    # These two adapters are connecting to H7 Polar devices
    chest_polar = adapter0.connect("F8:FF:5C:77:2A:A1", address_type=pygatt.BLEAddressType.random)
    #hand_polar = adapter1.connect("A0:9E:1A:5E:EF:F6")

    # USE THIS FOR CONNECTING TO THE NEWER H9 POLAR
    # H9_Polar = adapter.connect("F8:FF:5C:77:2A:A1", address_type=pygatt.BLEAddressType.random)

    chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(0)) #subscribing to heart rate measurement with the long letter-number ; when this line recieves new data, the callback function runs

    #hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(1))

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
    #adapter1.stop()