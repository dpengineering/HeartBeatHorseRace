from ObjectOrientedTest import *
from Player import *

# Device IDs (which you can find on the side of the polar adapters) correspond to a specific device address.
deviceMap = {
    "49A85121": "A0:9E:1A:49:A8:51", #horse2
    "5EEFF62F": "A0:9E:1A:5E:EF:F6", #horse3
    "A3DDF820": "C6:4B:DF:A5:36:0B", #horse1
    "9F43FF2B": "F8:FF:5C:77:2A:A1",
    "A3DDDD2F": "EF:FD:6F:EE:D7:81"
}

# Testing adapters
# Adapter 1

ADDRESS_TYPE = pygatt.BLEAddressType.random
adapter1 = pygatt.GATTToolBackend()
x = True

adapter1.start()

try:
    device1 = adapter1.connect("DF:CF:39:84:C2:78", address_type=pygatt.BLEAddressType.random)

except:
    print('An error has occurred! You might not have been holding the heart rate sensors properly, so '
          'try rerunning the program!')
    quit()


try:
    print("Heartrate found! Onto the next step.")
    device1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(1))
    while True:
        print('Finding heartrate...')
        sleep(20)
        if x is True:
            break

finally:
    adapter1.stop()