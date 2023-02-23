from ObjectOrientedTest import *
from Player import *

deviceMap = {
    "49A85121": "A0:9E:1A:49:A8:51", #horse2
    "5EEFF62F": "A0:9E:1A:5E:EF:F6", #horse3
    "A3DDF820": "C6:4B:DF:A5:36:0B",
    "9F43FF2B": "F8:FF:5C:77:2A:A1", #horse4
    "A3DDDD2F": "EF:FD:6F:EE:D7:81" #horse1
}

# Testing adapters

# Adapter 1

ADDRESS_TYPE = pygatt.BLEAddressType.random
adapter1 = pygatt.GATTToolBackend()

x = True

adapter1.start()

try:
    device1 = adapter1.connect("C6:4B:DF:A5:36:0B", address_type=pygatt.BLEAddressType.random)

except:
    print('error has occurred')

finally:

    print("done?")
try:
    device1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(1))
    while True:
        print('running')
        sleep(10)
        if x is True:
            break

finally:
    adapter1.stop()
    print('a')
    adapter1.stop()
    print('b')
    adapter1.start()
    print('c')



# # Adapter 2
#
# ADDRESS_TYPE = pygatt.BLEAddressType.random
# adapter2 = pygatt.GATTToolBackend()
#
# adapter2.start()
#
# device2 = adapter2.connect("EF:FD:6F:EE:D7:81", address_type=ADDRESS_TYPE)
#
#
# # Adapter 3
#
# ADDRESS_TYPE = pygatt.BLEAddressType.random
# adapter3 = pygatt.GATTToolBackend()
#
# adapter3.start()
#
# device3 = adapter3.connect("A0:9E:1A:5E:EF:F6", address_type=ADDRESS_TYPE)
#
# # Adapter 4
#
# ADDRESS_TYPE = pygatt.BLEAddressType.random
# adapter4 = pygatt.GATTToolBackend()
#
# adapter4.start()
#
# device4 = adapter4.connect("F8:FF:5C:77:2A:A1", address_type=ADDRESS_TYPE)