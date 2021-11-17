import sys
import time
import threading

import os
os.environ['DISPLAY'] = ":0.0"
os.environ['KIVY_WINDOW'] = 'sdl2'

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.MixPanel import MixPanel
from pidev.kivy import PauseScreen
from kivy.properties import ObjectProperty

from time import sleep
from datetime import datetime
from threading import Thread
from RPi_ODrive import ODrive_Ease_Lib
import odrive

od = odrive.find_any()
ax = ODrive_Ease_Lib.ODrive_Axis(od.axis0)

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
COUNTER_SCREEN_NAME = 'counter'

class MainApp(App):

    def build(self):

        return SCREEN_MANAGER

class MainScreen(Screen):

    normal_button = ObjectProperty(None)

    def start_sensor_thread(self):
        Thread(target=self.sensor_check).start()

    def sensor_check(self):
        while self.check_gpio() == False:
            sleep(0.01)
        print("You won!")
        ax.finished = True
        sleep(5)
        self.
        self.prepare_race()

    def check_gpio(self):
        if od.get_gpio_states() & 0b100 == 0:
            return True
        else:
            return False

    def prepare_race(self):
        if not ax.is_calibrated():
            print("calibrating...")
            ax.calibrate_with_current(60)

        ax.finished = False
        print("hi")
        ax.set_vel(1)
        sleep(10)
        ax.set_vel(0)
        ax.set_vel_limit(0.5)
        ax.set_pos(ax.get_pos() - 0.5)
        sleep(5)
        ax.set_vel_limit(5)
        ax.set_home()
        sleep(1)

    def follow(self, f):
        f.seek(0, 2)
        while True:
            curr_line = f.readline()
            if not curr_line:
                sleep(1)
                curr_line = f.readline()
                if not curr_line:
                    return
            yield curr_line

    def get_diff(self, heart_rate):
        max = heart_rate[0]

        for element in heart_rate:
            print("Heart Rate is:", element)
            if element > max:
                max = element

        return diff

    def get_avg(self, heart_rate):
        print("Getting baseline...")
        total = 0
        for element in heart_rate:
            total += element

        avg = total / len(heart_rate)
        return avg

    def get_diff(self, heart_rate, baseline):
        max = heart_rate[0]

        for element in heart_rate:
            if element > max:
                max = element
        diff = max - baseline
        print("Max is:", max)
        print("Baseline is:", baseline)
        print("Difference is:", diff)
        return diff

    def read_btle(self, out):
        # A0:9E:1A:5E:EF:F6 represents MAC Address of Polar H7 device
        os.system("gatttool -b A0:9E:1A:5E:EF:F6 --char-write-req --handle=0x0013 --value=0100 --listen > " + out)

    def run_normal_thread(self):
        self.counter_screen_action()
        Thread(target=self.run_normal_setting).start()

    def run_normal_setting(self):
        self.prepare_race()
        baseline = 0
        self.start_sensor_thread()

        output_filename = "hr_output_" + str(datetime.now().strftime("%m-%d-%Y")) + ".txt"
        bt_thread = Thread(target=lambda: self.read_btle(output_filename))
        bt_thread.daemon = True
        bt_thread.start()
        sleep(5)

        with open(output_filename, "r") as logfile:
            loglines = self.follow(logfile)
            count = 0
            baseline = 0
            heart_rate = []

            for line in loglines:
                hr_in_hex = line[39:41]

                if ax.finished:
                    break

                if count != 10 and baseline == 0:
                    heart_rate.append(int(hr_in_hex, 16))
                    print(heart_rate[count])
                    count += 1
                    sleep(0.5)

                elif count == 10 and baseline == 0:
                    print("Getting average...")
                    avg = self.get_avg(heart_rate)
                    baseline += 1
                    heart_rate.clear()
                    count = 0

                elif count != 5:

                    heart_rate.append(int(hr_in_hex, 16))
                    count += 1
                    sleep(0.5)
                elif count == 5:

                    diff = self.get_diff(heart_rate, avg)
                    count = 0

                    if diff <= 1:
                        ax.set_vel(-0.1)
                        print("Low Setting")
                        print("Velocity is:", ax.get_vel())

                    elif diff > 30:
                        ax.set_vel(-1)
                        print("Max Setting")
                        print("Velocity is:", ax.get_vel())

                    else:
                        ax.set_vel(diff / (-30))
                        print("Normal Setting")
                        print("Velocity is:", ax.get_vel())

                    count = 0
                    heart_rate.clear()

    def run_zen_setting(self):
        self.counter_screen_action()
        self.prepare_race()
        baseline = 0
        self.start_sensor_thread()

        output_filename = "hr_output_" + str(datetime.now().strftime("%m-%d-%Y")) + ".txt"
        bt_thread = Thread(target=lambda: self.read_btle(output_filename))
        bt_thread.daemon = True
        bt_thread.start()
        sleep(5)

        with open(output_filename, "r") as logfile:
            loglines = self.follow(logfile)
            count = 0
            baseline = 0
            heart_rate = []

            for line in loglines:
                hr_in_hex = line[39:41]

                if ax.finished:
                    break

                if count != 10 and baseline == 0:
                    heart_rate.append(int(hr_in_hex, 16))
                    print(heart_rate[count])
                    count += 1
                    sleep(0.5)

                elif count == 10 and baseline == 0:
                    print("Getting average...")
                    avg = self.get_avg(heart_rate)
                    baseline += 1
                    heart_rate.clear()
                    count = 0

                elif count != 5:

                    heart_rate.append(int(hr_in_hex, 16))
                    count += 1
                    sleep(0.5)

                elif count == 5:

                    diff = self.get_diff(heart_rate, avg)
                    count = 0

                    if diff <= 1:
                        ax.set_vel(-1)
                        print("Low Setting")
                        print("Velocity is:", ax.get_vel())

                    elif diff > 30:
                        ax.set_vel(-0.1)
                        print("Max Setting")
                        print("Velocity is:", ax.get_vel())

                    else:
                        ax.set_vel(diff / (-30))
                        print("Normal Setting")
                        print("Velocity is:", ax.get_vel())

                    count = 0
                    heart_rate.clear()

    def counter_screen_action(self):
        print("Switching Screen...")
        SCREEN_MANAGER.current = COUNTER_SCREEN_NAME

class CounterScreen(Screen):

    counter_button = ObjectProperty(None)

    #def __init__(self, **kwargs):
        #super(CounterScreen, self).__init__(**kwargs)
        #self.countdown()

    def run_countdown_thread(self):
        Thread(target=self.countdown).start()

    def countdown(self):
        counter = int(self.counter_button.text)
        sleep(1)
        while counter > 0:
            counter -= 1
            sleep(1)
            self.counter_button.text = str(counter)

    def transition_back(self):

        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

Builder.load_file('main.kv')
Builder.load_file('CounterScreen.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(CounterScreen(name=COUNTER_SCREEN_NAME))


def send_event(event_name):
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()

if __name__ == '__main__':
    MainApp().run()