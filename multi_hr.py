import pygatt
from binascii import hexlify
import time

adapter0 = pygatt.BGAPIBackend()
#adapter1 = pygatt.GATTToolBackend()


def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    #print("Received data: %s" % hexlify(value))
    #self.current_heartrate = (int(hexlify(value)[2:4], 16))
    print("Player Heart Rate: %s" % (int(hexlify(value)[2:4], 16)))


try:
    adapter0.start()
    #adapter1.start()
    #chest_polar = adapter0.connect("A0:9E:1A:49:A8:51")
    hand_polar = adapter0.connect("A0:9E:1A:5E:EF:F6")

    #chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(0))
                     
    hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data)

    # The subscription runs on a background thread. You must stop this main
    # thread from exiting, otherwise you will not receive any messages, and
    # the program will exit. Sleeping in a while loop like this is a simple
    # solution that won't eat up unnecessary CPU, but there are many other
    # ways to handle this in more complicated program. Multi-threaded
    # programming is outside the scope of this README.
    while True:
        time.sleep(10)
finally:
    adapter0.stop()
    #adapter1.stop()
