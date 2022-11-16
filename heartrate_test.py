import pygatt
from binascii import hexlify
import time

# Each adapter finds a Bluetooth Serial Port connected to the Raspberry Pi

adapter0 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM2')
adapter1 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM3')
adapter2 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM4')


def handle_data_for_player(player_num):
    def handle_data(handle, value):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """
        # print("Received data: %s" % hexlify(value))
        #print(" " * (32 * player_num) + "Player %s Heart Rate: %s" % (player_num, int(hexlify(value)[2:4], 16)))

        # This sets each heart rate to a scaled value
        t = int(hexlify(value)[2:4], 16) / 20
        print("Player " + str(player_num) + "'s velocity is " + str(t))
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
    hand_polar = adapter1.connect("C6:4B:DF:A5:36:0B", address_type=pygatt.BLEAddressType.random)
    chest_polar2 = adapter2.connect("A0:9E:1A:49:A8:51")

    chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(0)) #subscribing to heart rate measurement with the long letter-number ; when this line recieves new data, the callback function runs
    hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(1))
    chest_polar2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(2))

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



