#
from binascii import hexlify
from odrive_helpers import *
import horserace_helpers

class Player:

    # Device IDs (which you can find on the side of the polar adapters) correspond to a specific device address.
    deviceMap = {
        "49A85121": "A0:9E:1A:49:A8:51", #horse2
        "5EEFF62F": "A0:9E:1A:5E:EF:F6", #horse3
        "A3DDF820": "C6:4B:DF:A5:36:0B", #horse1
        "9F43FF2B": "F8:FF:5C:77:2A:A1", #horse4
        "A3DDDD2F": "EF:FD:6F:EE:D7:81"
    }

    def __init__(self, deviceID, od, player_num,  axis, baseline_rate, mode):
        self.track_lap = True
        self.laps = 0
        self.velocity = 0
        self.deviceID = deviceID
        self.od = od
        self.player_num = player_num
        if player_num == 1 or player_num == 3:
            self.od_num = 2
        else:
            self.od_num = 8
        self.axis = axis
        self.is_playing = True
        self.is_backward = False
        self.laps = 0
        self.base_velo = 1
        self.heart_weight = 70
        self.baseline_rate = baseline_rate
        self.is_done = True
        self.mode = mode

    def handle_tick(self, value):
        if not self.is_done:
            if not self.is_backward:
                if not self.check_end_sensor():
                    if self.mode == 0:
                        self.move(value)
                    elif self.mode == 1:
                        self.steadymove(value)
                    else:
                        self.zenmove(value)

        else:
            self.axis.set_vel(0)

    def check_end_sensor(self):
        if digital_read(self.od, self.od_num) == 0:
            if self.is_done is False:
                if not self.is_backward:
                    print("sensor hit")
                    self.axis.set_vel(1.4)
                    self.track_laps()
                    self.is_backward = True
                    sleep(0.5)
                    self.axis.wait_for_motor_to_stop()
                    if digital_read(self.od, self.od_num) != 0:
                        self.track_lap = True
                        self.is_backward = False
                    else:
                        self.check_end_sensor()
            else:
                self.axis.set_vel(0)
        else:
            return False

    def move(self, value):

        print("Heart rate is " + str(int(hexlify(value)[2:4], 16)))
        data = int(hexlify(value)[2:4], 16)
        t = (data - self.baseline_rate) / self.heart_weight

        self.velocity = (self.base_velo + t) * -1
        if self.velocity > 0:
            self.velocity = 0

        if not self.heartrate_is_real(data):
            self.velocity = self.base_velo * -1

        print("Player" +str(self.player_num) + " velocity is " + str(self.velocity))

        self.axis.set_vel(self.velocity)

    # Zenmove and Steadymove are two different types of race modes that are currently not used in the exhibit.
    # The math has already been done for you to implement them into the exhibit, but we didn't find it necessary.
    # The function 'move' (above) already does everything we want.
    def zenmove(self, value):

        print("Heart rate is " + str(int(hexlify(value)[2:4], 16)))
        data = int(hexlify(value)[2:4], 16)
        t = (self.baseline_rate - data) / self.heart_weight

        self.velocity = (self.base_velo + t) * -1
        if self.velocity > 0:
            self.velocity = 0

        if not self.heartrate_is_real(data):
            self.velocity = self.base_velo * -1

        print("Player" +str(self.player_num) + " velocity is " + str(self.velocity))

        self.axis.set_vel(self.velocity)

    def steadymove(self, value):

        print("Heart rate is " + str(int(hexlify(value)[2:4], 16)))
        data = int(hexlify(value)[2:4], 16)
        t = (horserace_helpers.steadymove_baseline - abs(self.baseline_rate - data)) / self.heart_weight

        self.velocity = (self.base_velo + t) * -1
        if self.velocity > 0:
            self.velocity = 0

        if not self.heartrate_is_real(data):
            self.velocity = self.base_velo * -1

        print("Player" +str(self.player_num) + " velocity is " + str(self.velocity))

        self.axis.set_vel(self.velocity)

    # This checks and/or adds the laps using the sensors at the end.
    def track_laps(self):
        if self.track_lap is True:
            self.track_lap = False
            self.laps += 1
            if self.laps >= horserace_helpers.total_laps:
                self.axis.set_vel(2)
                self.is_backward = True
                self.axis.wait_for_motor_to_stop()

    def game_done(self):
        self.is_done = True

    def start_game(self):
        self.is_done = False


    def get_laps(self):
        return self.laps

    def heartrate_is_real(self, heartrate):
        if heartrate > 30:
            if heartrate < 220:
                return True
        else:
            return False