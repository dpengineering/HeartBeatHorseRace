import pygatt
from binascii import hexlify
from time import sleep
from odrive_helpers import *
from threading import Thread

class Player:

    deviceMap = {
        "49A85121": "A0:9E:1A:49:A8:51",
        "5EEFF62F": "A0:9E:1A:5E:EF:F6",
        "A3DDF820": "C6:4B:DF:A5:36:0B",
        "9F43FF2B": "F8:FF:5C:77:2A:A1", #horse2
        "A3DDDD2F": "EF:FD:6F:EE:D7:81" #horse1
    }

    def __init__(self, deviceID, od, axis):
        self.deviceID = deviceID
        self.od = od
        self.axis = axis
        self.is_playing = True

    def check_end_sensor_player_version(self, horse, od_name, pin_number):
        if digital_read(od_name, pin_number) == 0:  # ==0 means the sensor is on and sensing; this is for horse 1
            print("sensor hit")
            horse.set_vel(0)
            sleep(.5)
            horse.set_rel_pos_traj(1, 1, 1, 1)
            #horse.wait_for_motor_to_stop()
    def check_sensors_player_version(self):
        while True:
            self.check_end_sensor_player_version(horse1, od_2, 2)
            sleep(.1)
    def thread_check_all_sensors_player_version(self):
        Thread(target=self.check_sensors_player_version, daemon=True).start()

    def heart_rate_average(self, lst):
        return sum(lst) / len(lst)

    def handle_data_for_axis(self, count, lst, pin_num):
        def handle_data(handle, value):
            """
            handle -- integer, characteristic read handle the data was received on
            value -- bytearray, the data returned in the notification
            """

            nonlocal count
            nonlocal lst
            speed_factor = 3
            #dump_err2000/a + a + 33ors(od)
            #print("Received data: %s" % hexlify(value))
            print("Player Heart Rate: %s" % (int(hexlify(value)[2:4], 16)))
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
                speed = ((10*((Crate-average)/(maxSpeed-average))) + 1)/5

                accel = 2
                if self.is_playing:

                    if speed == 0:
                        speed = 0
                        self.axis.set_ramped_vel(-speed, accel)

                    if 1/speed_factor < speed < 11/speed_factor:
                        speed = speed
                        self.axis.set_ramped_vel(-speed, accel)

                    if speed < 1/speed_factor:
                        speed = 1/speed_factor
                        self.axis.set_ramped_vel(-speed, accel)

                    if speed > 11/speed_factor:
                        speed = 11/speed_factor
                        self.axis.set_ramped_vel(-speed, accel)

                    print("Speed: ", speed)
                if digital_read(self.od, pin_num) == 0:
                    self.axis.set_vel(2)
                    sleep(1)
                    print("player is now done with game")
                    self.axis.set_vel(0)
                    self.is_playing = False

        return handle_data
    
def home_all_horses():
        horses = [horse1, horse2, horse3, horse4]
        for horse in horses:
            horse.set_ramped_vel(1, 1)
        sleep(1)
        for horse in horses:
            horse.wait_for_motor_to_stop()# waiting until motor slowly hits wall
        for horse in horses:
            horse.set_pos_traj(horse.get_pos() - 0.5, 1, 2, 1)
        sleep(3)  # allows motor to start moving to offset position
        for horse in horses:
            horse.wait_for_motor_to_stop()
        for horse in horses:
            horse.set_home()
            
            
if __name__ == "__main__":
    od_1 = find_odrive(serial_number="208D3388304B")
    od_2 = find_odrive(serial_number="20553591524B")
    horse1 = ODriveAxis(od_2.axis0, current_lim=10, vel_lim=10)
    horse2 = ODriveAxis(od_2.axis1, current_lim=10, vel_lim=10)
    horse3 = ODriveAxis(od_1.axis0, current_lim=10, vel_lim=10)
    horse4 = ODriveAxis(od_1.axis1, current_lim=10, vel_lim=10)
    home_all_horses()
    
    
    adapter1 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM2')
    adapter2 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM3')
    #player = Player("EF:FD:6F:EE:D7:81", od_2, horse1)
    player1 = Player("EF:FD:6F:EE:D7:81", od_2, horse1)
    player2 = Player("F8:FF:5C:77:2A:A1", od_1, horse3)
    try:
        
        adapter1.start()
        adapter2.start()

        # These two adapters are connecting to H7 Polar devices
        # chest_polar = adapter0.connect("A0:9E:1A:49:A8:51")
        #hand_polar = adapter0.connect(player.deviceID, address_type=pygatt.BLEAddressType.random)
        hand_polar1 = adapter1.connect(player1.deviceID, address_type=pygatt.BLEAddressType.random)
        hand_polar2 = adapter2.connect(player2.deviceID, address_type=pygatt.BLEAddressType.random)
        # USE THIS FOR CONNECTING TO THE NEWER H9 POLAR
        # H9_Polar = adapter.connect("F8:FF:5C:77:2A:A1", address_type=pygatt.BLEAddressType.random)

        # chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(0))

        # ax.set_vel(5)
        dump_errors(od_2)

        hand_polar1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=player1.handle_data_for_axis(0, [], 2))
        hand_polar2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=player2.handle_data_for_axis(0, [], 2))                               

        #hand_polar1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_axis(ax1, 0, []))        # The subscription runs on a background thread. You must stop this main
        # thread from exiting, otherwise you will not receive any messages, and
        # the program will exit. Sleeping in a while loop like this is a simple
        # solution that won't eat up unnecessary CPU, but there are many other
        # ways to handle this in more complicated program. Multi-threaded
        # programming is outside the scope of this README.
        while player1.is_playing or player2.is_playing:
            sleep(1)
            print("still playing")
    finally:
        print("exited 'try' code")
        adapter1.stop()
        adapter2.stop()
        #adapter3.stop()
        #adapter4.stop()
        horse1.set_vel(0)
        horse3.set_vel(0)
        #horse3.set_vel(0)
        #horse4.set_vel(0)
        horse1.idle()
        horse2.idle()
        horse3.idle()
        horse4.idle()
        # adapter1.stop()

