import os
import sys
from Player import Player
import pygatt
import kivy
from binascii import hexlify

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

os.environ['DISPLAY'] = ":0.0"
# os.environ['KIVY_WINDOW'] = 'egl_rpi'

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from odrive_helpers import digital_read
from threading import Thread
from time import sleep
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.clock import Clock
import kivy

from pidev.MixPanel import MixPanel
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
from pidev.kivy import DPEAButton
from pidev.kivy import ImageButton

sys.path.append("/home/soft-dev/Documents/dpea-odrive/")

from odrive_helpers import *
import time
import Player

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
TRAJ_SCREEN_NAME = 'traj'
GPIO_SCREEN_NAME = 'gpio'
ADMIN_SCREEN_NAME = 'admin'
BEGINNING_SCREEN_NAME = 'beginning'
BASELINE_SCREEN_NAME = 'baseline'
RUN_SCREEN_NAME = 'run'

od_1 = find_odrive(serial_number="208D3388304B")
od_2 = find_odrive(serial_number="20553591524B")

assert od_1.config.enable_brake_resistor is True, "Check for faulty brake resistor."
assert od_2.config.enable_brake_resistor is True, "Check for faulty brake resistor."

# axis0 and axis1 correspond to M0 and M1 on the ODrive
# You can also set the current limit and velocity limit when initializing the axis

horse1 = ODriveAxis(od_2.axis0, current_lim=10, vel_lim=10)
horse2 = ODriveAxis(od_2.axis1, current_lim=10, vel_lim=10)
horse3 = ODriveAxis(od_1.axis0, current_lim=10, vel_lim=10)
horse4 = ODriveAxis(od_1.axis1, current_lim=10, vel_lim=10)

# digital_read(od, 2) #od defined after od is defined
# Basic motor tuning, for more precise tuning,
# follow this guide: https://docs.odriverobotics.com/v/latest/control.html#tuning

horse1.set_gains()
horse2.set_gains()
horse3.set_gains()
horse4.set_gains()

# Checks the ODrive Calibraton
if not horse1.is_calibrated():
    print("calibrating horse1...")
    horse1.calibrate_with_current_lim(15)
if not horse2.is_calibrated():
    print("calibrating horse2...")
    horse2.calibrate_with_current_lim(15)
if not horse3.is_calibrated():
    print("calibrating horse3...")
    horse3.calibrate_with_current_lim(15)
if not horse4.is_calibrated():
    print("calibrating horse4...")
    horse4.calibrate_with_current_lim(15)


# Homes the Horses to Left Side
horses = [horse1, horse2, horse3, horse4]
for horse in horses:
    horse.set_ramped_vel(1, 1)
sleep(1)
for horse in horses:
    horse.wait_for_motor_to_stop()  # waiting until motor slowly hits wall
for horse in horses:
    horse.set_pos_traj(horse.get_pos() - 0.5, 1, 2, 1)
sleep(3)  # allows motor to start moving to offset position
for horse in horses:
    horse.wait_for_motor_to_stop()
for horse in horses:
    horse.set_home()


print("Current Limit Horse1: ", horse1.get_current_limit())
print("Velocity Limit Horse1: ", horse1.get_vel_limit())
print("Current Limit Horse2: ", horse2.get_current_limit())
print("Velocity Limit Horse2: ", horse2.get_vel_limit())
print("Current Limit Horse3: ", horse3.get_current_limit())
print("Velocity Limit Horse3: ", horse3.get_vel_limit())
print("Current Limit Horse4: ", horse4.get_current_limit())
print("Velocity Limit Horse4: ", horse4.get_vel_limit())

horse1.set_vel(0)
horse2.set_vel(0)
horse3.set_vel(0)
horse4.set_vel(0)

dump_errors(od_1)
dump_errors(od_2)

od_1.clear_errors()
od_2.clear_errors()

od_1.axis0.controller.config.enable_overspeed_error = False
od_1.axis1.controller.config.enable_overspeed_error = False
od_2.axis0.controller.config.enable_overspeed_error = False
od_2.axis1.controller.config.enable_overspeed_error = False

player1 = Player("C6:4B:DF:A5:36:0B", od_1, horse1)
player2 = Player("A0:9E:1A:49:A8:51", od_1, horse2)
player3 = Player("A0:9E:1A:5E:EF:F6", od_2, horse3)
player4 = Player("F8:FF:5C:77:2A:A1", od_2, horse4)

numberOfPlayers = 0
baseline1 = 0
baseline2 = 0
baseline3 = 0
baseline4 = 0

baseline1List = []
baseline2List = []
baseline3List = []
baseline4List = []

global vernier1
global vernier2
global vernier3
global vernier4

h1_laps = 0
h2_laps = 0
h3_laps = 0
h4_laps = 0

h1_timer = time.time()
h2_timer = time.time()
h3_timer = time.time()
h4_timer = time.time()

def heartrate_is_real(heartrate):
    if heartrate > 30:
        if heartrate < 170:
            return True
    else:
        return False

def setup(player_num):
    def velocity_movement(handle, value):
        base_velo = 0.5  # will get this from something else later
        heart_weight = 70  # will set at some point
        baseline_rate = 60  # get from something else as well

        print("Heart rate is " + str(int(hexlify(value)[2:4], 16)))
        data = int(hexlify(value)[2:4], 16)
        t = (data - baseline_rate) / heart_weight

        velocity = (base_velo + t) * -1
        if -2 < ((base_velo + ((data - baseline1) / heart_weight)) * -1) < 0:
            velocity1 = ((base_velo + ((data - baseline1) / heart_weight)) * -1)
        else:
            velocity1 = 0
            print('1 positive velocity')
        if -2 < ((base_velo + ((data - baseline2) / heart_weight)) * -1) < 0:
            velocity2 = ((base_velo + ((data - baseline2) / heart_weight)) * -1)
        else:
            velocity2 = 0
            print('2 positive velocity')
        if -2 < ((base_velo + ((data - baseline3) / heart_weight)) * -1) < 0:
            velocity3 = ((base_velo + ((data - baseline3) / heart_weight)) * -1)
        else:
            velocity3 = 0
            print('3 positive velocity')
        if -2 < ((base_velo + ((data - baseline4) / heart_weight)) * -1) < 0:
            velocity4 = ((base_velo + ((data - baseline4) / heart_weight)) * -1)
        else:
            velocity4 = 0
            print('3 positive velocity')

        if not heartrate_is_real(data):
            velocity = base_velo * -1

        print("Player 1's velocity is " + str(velocity1))
        print("Player 2's velocity is " + str(velocity2))
        print("Player 3's velocity is " + str(velocity3))
        print("Player 4's velocity is " + str(velocity4))

        if player_num == 1:
            horse1.set_vel(velocity1)
        elif player_num == 2:
            horse2.set_vel(velocity2)
        elif player_num == 3:
            horse3.set_vel(velocity3)
        else:
            horse4.set_vel(velocity4)

    print("hello?")

    def end_game():
        print("Player " + str(player_num) + " Wins!")

        vernier1.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        vernier2.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        vernier3.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
        vernier4.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")

        adapter1.stop()
        adapter2.stop()
        adapter3.stop()

        horse1.set_vel(0)
        horse2.set_vel(0)
        horse3.set_vel(0)
        horse4.set_vel(0)

        horse1.idle()
        horse2.idle()
        horse3.idle()
        horse4.idle()

    def track_laps():

        global h1_laps, h2_laps, h3_laps, h4_laps, h1_timer, h2_timer, h3_timer, h4_timer

        total_laps = 3

        buffer = 4

        if player_num == 1:
            if buffer < round((time.time() - h1_timer), 2):
                h1_laps += 1

                if h1_laps == total_laps:
                    end_game()

                h1_timer = time.time()
        elif player_num == 2:
            if buffer < round((time.time() - h2_timer), 2):
                h2_laps += 1

                if h2_laps == total_laps:
                    end_game()

                h2_timer = time.time()
        elif player_num == 3:
            if buffer < round((time.time() - h3_timer), 2):
                h3_laps += 1

                if h3_laps == total_laps:
                    end_game()

                h3_timer = time.time()
        else:
            if buffer < round((time.time() - h4_timer), 2):
                h4_laps += 1

                if h4_laps == total_laps:
                    end_game()

                h4_timer = time.time()

    def at_end():
        if player_num == 1:
            track_laps()
            horse1.set_vel(2)
            horse1.wait_for_motor_to_stop()
            horse1.set_vel(-0.8)

        elif player_num == 2:
            track_laps()
            horse2.set_vel(2)
            horse2.wait_for_motor_to_stop()
            horse2.set_vel(-0.8)
        elif player_num == 3:
            track_laps()
            horse3.set_vel(2)
            horse3.wait_for_motor_to_stop()
            horse3.set_vel(-0.8)
        else:
            track_laps()
            horse4.set_vel(2)
            horse4.wait_for_motor_to_stop()
            horse4.set_vel(-0.8)
        return

    def handle_tick(handle, value):

        if player_num == 1:
            horse = horse1
            if horse.get_vel() <= 0:
                if (digital_read(od_2, 2) == 0):
                    at_end()
                else:

                    velocity_movement(handle, value)
            else:
                print('not working')
                return

        elif player_num == 2:
            horse = horse2

            if horse.get_vel() <= 0:
                if (digital_read(od_2, 8) == 0):
                    at_end()
                else:

                    velocity_movement(handle, value)
            else:
                return
        elif player_num == 3:
            horse = horse3

            if horse.get_vel() <= 0:
                if (digital_read(od_1, 2) == 0):

                    at_end()
                else:

                    velocity_movement(handle, value)
            else:
                return
        else:
            horse = horse4

            if horse.get_vel() <= 0:
                if (digital_read(od_1, 8) == 0):

                    at_end()
                else:

                    velocity_movement(handle, value)
            else:
                return

    return handle_tick

def heartrate_baseline(player_num):
    def handle_data(handle, value):
        heartrate = int(hexlify(value)[2:4], 16)

        if heartrate_is_real(heartrate):
            if player_num == 1:
                baseline1List.append(heartrate)
            elif player_num == 2:
                baseline2List.append(heartrate)
            elif player_num == 3:
                baseline3List.append(heartrate)
            elif player_num == 4:
                baseline4List.append(heartrate)
            else:
                print('not good')
        else:
            print('unlucky')

    return handle_data


def average_heartrate(lst):
    if not len(lst) == 0:
        return sum(lst) / len(lst)
    else:
        return 'not averaged'


print("end of beginning")


class ProjectNameGUI(App):
    """
    Class to handle running the GUI Application
    """

    def build(self):
        """
        Build the application
        :return: Kivy Screen Manager instance
        """
        return SCREEN_MANAGER

    print("class created")


Window.clearcolor = (1, 1, 1, 1)  # White
adapter1 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM2')
adapter2 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM3')
adapter3 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM4')
adapter4 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM5')


class MainScreen(Screen):
    """
    Class to handle the main screen and its associated touch events
    """
    count = 0
    elapsed = ObjectProperty()

    def redraw(self, args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


    def run_players(self):
        # adapter3 = pygatt.BGAPIBackend()
        # adapter4 = pygatt.BGAPIBackend()
        player1 = Player("C6:4B:DF:A5:36:0B", od_1, horse1)
        # player2 = Player("F8:FF:5C:77:2A:A1", od_1, horse3)
        # player3 = Player("", od_1, horse3)
        # player4 = Player("", od_1, horse4)
        try:
            adapter1.start()
            # adapter2.start()
            # adapter3.start()
            # adapter4.start()
            hand_polar1 = adapter1.connect(player1.deviceID, address_type=pygatt.BLEAddressType.random)
            # hand_polar2 = adapter2.connect(player2.deviceID, address_type=pygatt.BLEAddressType.random)
            # hand_polar3 = adapter3.connect(player3.deviceID, address_type=pygatt.BLEAddressType.random)
            # hand_polar4 = adapter4.connect(player4.deviceID, address_type=pygatt.BLEAddressType.random)
            # dump_errors(od_2)
            # dump_errors(od_1)
            hand_polar1.subscribe("00002a37-0000-1000-8000-00805f9b34fb",
                                  callback=player1.handle_data_for_axis(0, [], 2))
            # hand_polar2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=player2.handle_data_for_axis(0, [], 2))
            # hand_polar3.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=player3.handle_data_for_axis(0, []))
            # hand_polar4.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=player4.handle_data_for_axis(0, []))
            # horse1_finished = False
            # horse2_finished = False
            # while not horse1_finished or not horse2_finished:
            #   if digital_read(od_2, 2) == 0:
            #        horse1.set_vel(2)
            #        sleep(1)
            #        horse1.set_vel(0)
            #        horse1_finished = True
            #    if digital_read(od_2, 8) == 0:
            #       horse2.set_vel(2)
            #       sleep(1)
            #       horse2.set_vel(0)
            #       horse2_finished = True
            #    sleep(.1)
            # horse1.set_rel_pos_traj(1, 1, 1, 1)
            # sleep(1)
            # horse1.wait_for_motor_to_stop()

            print("done with try code")
            while player1.is_playing:  # or player2.is_playing:
                sleep(1)
            # adapter1.stop()
            # YOU CAN ALSO TRY ADAPTER1.STOP SO THAT IT DOESN'T EXIT TRY CODE

        finally:
            print("exited 'try' code")
            adapter1.stop()
            adapter2.stop()
            # adapter3.stop()
            # adapter4.stop()
            horse1.set_vel(0)
            horse3.set_vel(0)
            # horse3.set_vel(0)
            # horse4.set_vel(0)
            horse1.idle()
            horse3.idle()
            horse3.idle()
            horse4.idle()

    def stop_time(self):
        self.horse1_running = False
        self.horse2_running = False
        self.horse3_running = False
        self.horse4_running = False
        self.start_time_button.disabled = False
        self.timer_status = False

    def start_time_thread(self):
        Thread(target=self.start_time, daemon=True).start()

    def start_time(self):
        # horse1_time = time()
        # horse2_time = time()
        # horse3_time = time()
        # horse4_time = time()
        start = time()
        print("Start: Seconds since epoch =", start)
        self.horse1_running = True
        self.horse2_running = True
        self.horse3_running = True
        self.horse4_running = True
        self.timer_status = True
        self.start_time_button.disabled = True
        while True:
            self.elapsed = str(round((time() - start), 2))
            if self.timer_status == False:
                # self.elapsed = 0
                # self.timer_horse1.text = self.elapsed
                # self.timer_horse2.text = self.elapsed
                # self.timer_horse3.text = self.elapsed
                # self.timer_horse4.text = self.elapsed
                break
            else:
                print("you have not pressed 'stop timer' yet")
            if digital_read(od_2, 2) == 1 and self.horse1_running:  # horse 1 is not sensing and variable reads True
                self.timer_horse1.text = self.elapsed
            else:
                print("horse 1 sensed")
                self.horse1_running = False
            if digital_read(od_2, 8) == 1 and self.horse2_running:  # horse 2 is not sensing
                self.timer_horse2.text = self.elapsed
            else:
                print("horse 2 sensed")
                self.horse2_running = False
            if digital_read(od_1, 2) == 1 and self.horse3_running:
                self.timer_horse3.text = self.elapsed
            else:
                print("horse 3 sensed")
                self.horse3_running = False
            if digital_read(od_1, 8) == 1 and self.horse4_running:
                self.timer_horse4.text = self.elapsed
            else:
                print("horse 4 sensed")
                self.horse4_running = False
            sleep(.03)

        # while digital_read(od_1, 8) == 1 & digital_read(od_1, 2) == 1 & digital_read(od_2, 8) == 1 & digital_read(od_2, 2) == 1:
        #    print("No sensors sensing")
        #    print("horse1_time = ", horse1_time )
        #    sleep(1)
        # while True:
        #     if digital_read(od_1, 8) == 1 & digital_read(od_1, 2) == 1 & digital_read(od_2, 8) == 1 & digital_read(od_2, 2) == 1:
        #         print("All sensors aren't sensing")
        #         self.elapsed = str(round((time() - start), 2))
        #         self.timer_horse1.text = self.elapsed
        #         self.timer_horse2.text = self.elapsed
        #         self.timer_horse3.text = self.elapsed
        #         self.timer_horse4.text = self.elapsed
        #         #self.ids.timer_horse1.text = str('four') #str(round(elapsed, 1))
        #         print(self.elapsed)
        #         sleep(0.05) #why ISN'T the timer reading every 0.5 seconds?
        #     else:
        #         print("a sensor is sensing, or there is an error")
        #         break

    # ----------------------------------------------------------------------------------------------------------------#
    # digital_read(od_1, 8) == 0:  # ==0 means the sensor is on and sensing; this is for horse 4
    # digital_read(od_1, 2) == 0:  # ==0 means the sensor is on and sensing; this is for horse 3
    # digital_read(od_2, 8) == 0:  # ==0 means the sensor is on and sensing; this is for horse 2
    # digital_read(od_2, 2) == 0:  # ==0 means the sensor is on and sensing; this is for horse 1

    def check_end_sensor(self, horse, od_name, pin_number):
        if digital_read(od_name, pin_number) == 0:  # ==0 means the sensor is on and sensing; this is for horse 1
            print("sensor hit")
            horse.set_vel(0)
            sleep(.5)
            horse.set_rel_pos_traj(1, 1, 1, 1)
            horse.wait_for_motor_to_stop()

    def check_all_sensors(self):
        while True:
            self.check_end_sensor(horse1, od_2, 2)
            self.check_end_sensor(horse2, od_2, 8)
            self.check_end_sensor(horse3, od_1, 2)
            self.check_end_sensor(horse4, od_1, 8)
            sleep(.1)

    def thread_check_all_sensors(self):
        Thread(target=self.check_all_sensors, daemon=True).start()

    def thread_end_sensor_horse1(self):
        Thread(target=self.end_sensor_horse1, daemon=True).start()

    def end_sensor_horse1(self):
        while True:
            # print("while True 1 running")
            sleep(.1)
            self.check_end_sensor(horse1, od_2, 2)
            # if digital_read(od_2, 2) == 0: # ==0 means the sensor is on and sensing; this is for horse 1
            #    print("sensor hit for horse1")
            #    horse1.set_vel(0)
            #    sleep(.5)
            #    print("slept")
            #    horse1.set_rel_pos_traj(1, 1, 1, 1)
            #    horse1.wait_for_motor_to_stop()
            # else:
            #    #print("sensor1 not currently being hit")
            #    sleep(.1)

    def thread_end_sensor_horse2(self):
        Thread(target=self.end_sensor_horse2, daemon=True).start()

    def end_sensor_horse2(self):
        while True:
            # print("while True 2 running")
            sleep(.1)
            self.check_end_sensor(horse2, od_2, 8)

    def thread_end_sensor_horse3(self):
        Thread(target=self.end_sensor_horse3, daemon=True).start()

    def end_sensor_horse3(self):
        while True:
            # print("while True 3 running")
            sleep(.1)
            self.check_end_sensor(horse3, od_1, 2)

    def thread_end_sensor_horse4(self):
        Thread(target=self.end_sensor_horse4, daemon=True).start()

    def end_sensor_horse4(self):
        while True:
            # print("while True 4 running")
            sleep(.1)
            self.check_end_sensor(horse4, od_1, 8)

    def switch_to_traj(self):
        SCREEN_MANAGER.transition.direction = "left"
        SCREEN_MANAGER.current = TRAJ_SCREEN_NAME

    def switch_to_gpio(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = GPIO_SCREEN_NAME

    def switch_to_beginning(self):
        SCREEN_MANAGER.transition.direction = "down"
        SCREEN_MANAGER.current = BEGINNING_SCREEN_NAME

    ##CONNECTED TO THE HOME BUTTON##

    def home_all_horses(self):
        horses = [horse1, horse2, horse3, horse4]
        for horse in horses:
            horse.set_ramped_vel(1, 1)
        sleep(1)
        for horse in horses:
            horse.wait_for_motor_to_stop()  # waiting until motor slowly hits wall
        for horse in horses:
            horse.set_pos_traj(horse.get_pos() - 0.5, 1, 2, 1)
        sleep(3)  # allows motor to start moving to offset position
        for horse in horses:
            horse.wait_for_motor_to_stop()
        for horse in horses:
            horse.set_home()

    # def thread_home_without_endstop(self):
    #    Thread(target=self.horse1_home_without_endstop, daemon=True).start()
    #    Thread(target=self.horse2_home_without_endstop, daemon=True).start()
    #    Thread(target=self.horse3_home_without_endstop, daemon=True).start()
    #    Thread(target=self.horse4_home_without_endstop, daemon=True).start()
    #   # self.horse1_home_without_endstop()
    #   # self.horse2_home_without_endstop()
    #   # self.horse3_home_without_endstop()
    #   # self.horse4_home_without_endstop( )
    #
    # def horse1_home_without_endstop(self):
    #    horse1.home_without_endstop(1, -.5)
    #    print("thread ran for horse1")
    # def horse2_home_without_endstop(self):
    #    horse2.home_without_endstop(1, -.5)
    #    print("thread ran for horse2")
    # def horse3_home_without_endstop(self):
    #    horse3.home_without_endstop(1, -.5)
    #    print("thread ran for horse3")
    # def horse4_home_without_endstop(self):
    #    horse4.home_without_endstop(1, -.5)
    #    print("thread ran for horse4")

    ##CONNECTED TO MOTOR TOGGLE BUTTON##
    def motor_toggle(self):
        # horse3.set_relative_pos(0)
        print(horse3.get_vel())
        # dump_errors(od)
        if horse3.get_vel() <= 0.2:
            if self.count % 2 == 0:
                horse3.set_rel_pos_traj(10, self.acceleration_slider.value, 10, self.acceleration_slider.value)
                print('If vel = 0 and count% = 0 : horse3.set_rel_pos_traj(-5, .5, 1, .5)')
                self.count += 1
            elif self.count % 2 == 1:
                horse3.set_rel_pos_traj(-10, self.acceleration_slider.value, 10, self.acceleration_slider.value)
                print('If vel = 0 and count% = 1 : horse3.set_rel_pos_traj(5, .5, 1, .5)')
                self.count += 1
            else:
                print("motor_toggle command malfunction")
        else:
            if self.count % 2 == 0:
                horse3.set_rel_pos_traj(5, self.acceleration_slider.value, self.velocity_slider_horse3.value,
                                        self.acceleration_slider.value)
                print('If vel = moving and count% = 0 : horse3.set_rel_pos_traj(5, .5, var, .5)')
                # horse3.set_vel_limit(self.velocity_slider.value)
                # horse3.set_relative_pos(-5)
                self.count += 1
            elif self.count % 2 == 1:
                horse3.set_rel_pos_traj(-5, self.acceleration_slider.value, self.velocity_slider_horse3.value,
                                        self.acceleration_slider.value)
                print('If vel = moving and count% = 1 : horse3.set_rel_pos_traj(-5, .5, var, .5)')
                # horse3.set_vel_limit(self.velocity_slider.value)
                # horse3.set_relative_pos(5)
                self.count += 1
            else:
                print("motor_toggle command malfunction")

    def admin_action(self):
        """
        Hidden admin button touch event. Transitions to passCodeScreen.
        This method is called from pidev/kivy/PassCodeScreen.kv
        :return: None
        """
        SCREEN_MANAGER.current = 'passCode'

    print("screen 1 created")

    def quit(self):
        print("Exit")
        quit()


class BeginningScreen(Screen):
    def switch_screen1(self):
        SCREEN_MANAGER.transition.direction = "down"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def two_players(self):
        global numberOfPlayers
        if numberOfPlayers == 2:
            SCREEN_MANAGER.transition.direction = "left"
            SCREEN_MANAGER.current = BASELINE_SCREEN_NAME

            return numberOfPlayers

        else:

            adapter1.start()
            print('adapter1 started')
            adapter2.start()
            print('adapter2 started')

            SCREEN_MANAGER.transition.direction = "left"
            SCREEN_MANAGER.current = BASELINE_SCREEN_NAME

            numberOfPlayers = 2
            return numberOfPlayers

    def three_players(self):
        global numberOfPlayers
        if numberOfPlayers == 3:
            SCREEN_MANAGER.transition.direction = "left"
            SCREEN_MANAGER.current = BASELINE_SCREEN_NAME

            return numberOfPlayers

        elif numberOfPlayers == 2:
            adapter3.start()
            print('adapter3 started')

            SCREEN_MANAGER.transition.direction = "left"
            SCREEN_MANAGER.current = BASELINE_SCREEN_NAME

            numberOfPlayers = 3
            return numberOfPlayers

        else:
            adapter1.start()
            print('adapter1 started')
            adapter2.start()
            print('adapter2 started')
            adapter3.start()
            print('adapter3 started')

            SCREEN_MANAGER.transition.direction = "left"
            SCREEN_MANAGER.current = BASELINE_SCREEN_NAME

            numberOfPlayers = 3
            return numberOfPlayers

    def four_players(self):
        global numberOfPlayers
        if numberOfPlayers == 4:
            SCREEN_MANAGER.transition.direction = "left"
            SCREEN_MANAGER.current = BASELINE_SCREEN_NAME

            return numberOfPlayers

        elif numberOfPlayers == 3:
            adapter4.start()
            print('adapter4 started')

            SCREEN_MANAGER.transition.direction = "left"
            SCREEN_MANAGER.current = BASELINE_SCREEN_NAME

            numberOfPlayers = 4
            return numberOfPlayers

        elif numberOfPlayers == 2:
            adapter3.start()
            print('adapter3 started')
            adapter4.start()
            print('adapter4 started')

            SCREEN_MANAGER.transition.direction = "left"
            SCREEN_MANAGER.current = BASELINE_SCREEN_NAME

            numberOfPlayers = 4
            return numberOfPlayers

        else:
            adapter1.start()
            print('adapter1 started')
            adapter2.start()
            print('adapter2 started')
            adapter3.start()
            print('adapter3 started')
            adapter4.start()
            print('adapter4 started')

            SCREEN_MANAGER.transition.direction = "left"
            SCREEN_MANAGER.current = BASELINE_SCREEN_NAME

            numberOfPlayers = 4
            return numberOfPlayers

    print("Beginning Screen Created")


class BaselineScreen(Screen):
    def find_baseline(self):
        global baseline1, baseline2, baseline3, baseline4
        global vernier1, vernier2, vernier3, vernier4
        if numberOfPlayers == 2:
            i = 0
            vernier1 = adapter1.connect(player1.deviceID, address_type=pygatt.BLEAddressType.random)
            print('vernier1 connected')
            vernier2 = adapter2.connect(player2.deviceID)
            print('vernier2 connected')

            while i < 3:
                vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(1))
                vernier2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(2))
                sleep(1)
                i += 1

            vernier1.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
            vernier2.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")

            baseline1 = round(average_heartrate(baseline1List))
            baseline2 = round(average_heartrate(baseline2List))

            self.ids.player1Baseline.text = str(baseline1)
            self.ids.player2Baseline.text = str(baseline2)
            self.ids.player3Baseline.text = "No Player!"
            self.ids.player4Baseline.text = "No Player!"

            sleep(5)

            SCREEN_MANAGER.transition.direction = "right"
            SCREEN_MANAGER.current = RUN_SCREEN_NAME

        elif numberOfPlayers == 3:
            i = 0
            vernier1 = adapter1.connect(player1.deviceID, address_type=pygatt.BLEAddressType.random)
            print('vernier1 connected')
            vernier2 = adapter2.connect(player2.deviceID)
            print('vernier2 connected')
            vernier3 = adapter3.connect(player3.deviceID)
            print('vernier3 connected')

            while i < 3:
                vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(1))
                vernier2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(2))
                vernier3.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(3))
                sleep(1)
                print(baseline3List)
                i += 1

            vernier1.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
            vernier2.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")
            vernier3.unsubscribe("00002a37-0000-1000-8000-00805f9b34fb")

            baseline1 = round(average_heartrate(baseline1List))
            baseline2 = round(average_heartrate(baseline2List))
            baseline3 = round(average_heartrate(baseline3List))

            self.ids.player1Baseline.text = str(baseline1)
            self.ids.player2Baseline.text = str(baseline2)
            self.ids.player3Baseline.text = str(baseline3)
            self.ids.player3Baseline.text = "No Player!"

            sleep(5)

            SCREEN_MANAGER.transition.direction = "right"
            SCREEN_MANAGER.current = RUN_SCREEN_NAME

        elif numberOfPlayers == 4:  # WIP
            vernier1 = adapter1.connect(player1.deviceID, address_type=pygatt.BLEAddressType.random)
            print('vernier1 connected')
            vernier2 = adapter2.connect(player2.deviceID)
            print('vernier2 connected')
            vernier3 = adapter3.connect(player3.deviceID)
            print('vernier3 connected')
            vernier4 = adapter4.connect(player4.deviceID, address_type=pygatt.BLEAddressType.random)
            print('vernier4 connected')

            vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(1))
            vernier2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(2))
            vernier3.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(3))
            vernier4.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=heartrate_baseline(4))

            adapter1.stop()
            adapter2.stop()
            adapter3.stop()
            adapter4.stop()

        else:
            print('not working L')
            return

        return baseline1, baseline2, baseline3, baseline4, vernier1, vernier2

    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = BEGINNING_SCREEN_NAME

    print("Baseline Screen Created")


class RunScreen(Screen):

    def update_baseline(self):
        self.ids.player1Baseline.text = str(baseline1)
        self.ids.player2Baseline.text = str(baseline2)
        self.ids.player3Baseline.text = str(baseline3)
        self.ids.player4Baseline.text = str(baseline4)

    def start_game(self):
        t = "5"
        while int(t) > 0:
            t = str(int(t) - 1)
            sleep(1)
        self.ids.count.text = "GO!"
        sleep(.5)
        try:
            vernier1.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(1))
            vernier2.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(2))
            #vernier3.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=setup(3))
            while True:
                time.sleep(10)
                print("while True is running")
        finally:
            adapter1.stop()
            adapter2.stop()
            adapter3.stop()
            adapter4.stop()



class TrajectoryScreen(Screen):
    """
    Class to handle the trajectory control screen and its associated touch events
    """

    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "right"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def submit_trapezoidal_traj(self):
        horse1.set_vel_limit(10)
        horse2.set_vel_limit(10)
        horse3.set_vel_limit(10)
        horse4.set_vel_limit(10)
        horse1.set_pos_traj(int(self.target_position.text), int(self.acceleration.text), int(self.target_speed.text),
                            int(self.deceleration.text))  # position 5, acceleration 1 turn/s^2, target velocity 10 turns/s, deceleration 1 turns/s^2
        horse2.set_pos_traj(int(self.target_position.text), int(self.acceleration.text), int(self.target_speed.text),
                            int(self.deceleration.text))  # position 5, acceleration 1 turn/s^2, target velocity 10 turns/s, deceleration 1 turns/s^2
        horse3.set_pos_traj(int(self.target_position.text), int(self.acceleration.text), int(self.target_speed.text),
                            int(self.deceleration.text))  # position 5, acceleration 1 turn/s^2, target velocity 10 turns/s, deceleration 1 turns/s^2
        horse4.set_pos_traj(int(self.target_position.text), int(self.acceleration.text), int(self.target_speed.text),
                            int(self.deceleration.text))  # position 5, acceleration 1 turn/s^2, target velocity 10 turns/s, deceleration 1 turns/s^2


class GPIOScreen(Screen):
    """
    Class to handle the GPIO screen and its associated touch/listening events
    """

    # horseNUM.home_with_endstop(self, vel, offset, min_gpio_num):

    def homing_switch(self):
        horses = [horse1, horse2, horse3, horse4]
        for horse in horses:
            horse.set_ramped_vel(1, 1)
        sleep(1)
        for horse in horses:
            horse.home_with_endstop(1, 1, 2)

    def switch_screen(self):
        SCREEN_MANAGER.transition.direction = "left"
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    print("gpio screen created")


class AdminScreen(Screen):
    """
    Class to handle the AdminScreen and its functionality
    """

    def __init__(self, **kwargs):
        """
        Load the AdminScreen.kv file. Set the necessary names of the screens for the PassCodeScreen to transition to.
        Lastly super Screen's __init__
        :param kwargs: Normal kivy.uix.screenmanager.Screen attributes
        """
        Builder.load_file('AdminScreen.kv')

        PassCodeScreen.set_admin_events_screen(
            ADMIN_SCREEN_NAME)  # Specify screen name to transition to after correct password
        PassCodeScreen.set_transition_back_screen(
            MAIN_SCREEN_NAME)  # set screen name to transition to if "Back to Game is pressed"

        super(AdminScreen, self).__init__(**kwargs)

        print("admin screen created")

    @staticmethod
    def transition_back():
        """
        Transition back to the main screen
        :return:
        """
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    @staticmethod
    def shutdown():
        """
        Shutdown the system. This should free all steppers and do any cleanup necessary
        :return: None
        """
        os.system("sudo shutdown now")

    @staticmethod
    def exit_program():
        """
        Quit the program. This should free all steppers and do any cleanup necessary
        :return: None
        """
        quit()

    print("static methods created")


"""
Widget additions
"""

Builder.load_file('main.kv')
Builder.load_file('BeginningScreen.kv')
Builder.load_file('BaselineScreen.kv')
Builder.load_file('RunScreen.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(TrajectoryScreen(name=TRAJ_SCREEN_NAME))
SCREEN_MANAGER.add_widget(GPIOScreen(name=GPIO_SCREEN_NAME))
SCREEN_MANAGER.add_widget(BeginningScreen(name=BEGINNING_SCREEN_NAME))
SCREEN_MANAGER.add_widget(BaselineScreen(name=BASELINE_SCREEN_NAME))
SCREEN_MANAGER.add_widget(RunScreen(name=RUN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(PassCodeScreen(name='passCode'))
SCREEN_MANAGER.add_widget(PauseScreen(name='pauseScene'))
SCREEN_MANAGER.add_widget(AdminScreen(name=ADMIN_SCREEN_NAME))
print("various screens created")

"""
MixPanel
"""


def send_event(event_name):
    """
    Send an event to MixPanel without properties
    :param event_name: Name of the event
    :return: None
    """
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()
    print("mix panel")


if __name__ == "__main__":
    # send_event("Project Initialized")
    # Window.fullscreen = 'auto'
    print("done setting up")
    ProjectNameGUI().run()
