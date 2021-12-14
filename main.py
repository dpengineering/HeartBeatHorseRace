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
import odrive
from RPi_ODrive import ODrive_Ease_Lib

od = odrive.find_any()
ax = ODrive_Ease_Lib.ODrive_Axis(od.axis0)
baseline_1 = 0

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
GAME_SCREEN_NAME = 'game'
COUNTER_SCREEN_NAME = 'counter'
INSTRUCTIONS_SCREEN_NAME = 'instructions'
TEST_SCREEN_NAME = 'test'
CHAOS_SCREEN_NAME = 'chaos'
STEADY_SCREEN_NAME = 'steady'
ZEN_SCREEN_NAME = 'zen'

class MainApp(App):

    def build(self):
        return SCREEN_MANAGER




class MainScreen(Screen):

    exit_button = ObjectProperty(None)
    instructions_button = ObjectProperty(None)
    continue_button = ObjectProperty(None)

    def instructions_screen(self):
        SCREEN_MANAGER.current = INSTRUCTIONS_SCREEN_NAME

    def game_screen(self):
        SCREEN_MANAGER.current = GAME_SCREEN_NAME

    def exit_program(self):
        quit()




class InstructionsScreen(Screen):

    def main_screen(self):
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME


class GameScreen(Screen):

    check = 0

    back_button_2 = ObjectProperty(None)
    baseline_button = ObjectProperty(None)
    normal_button = ObjectProperty(None)
    zen_button = ObjectProperty(None)
    chaos_button = ObjectProperty(None)

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

    def enable_buttons(self):
        self.normal_button.disabled = False
        self.chaos_button.disabled = False
        self.zen_button.disabled = False

    def disable_buttons(self):
        self.normal_button.disabled = True
        self.chaos_button.disabled = True
        self.zen_button.disabled = True

    def read_btle(self, out):
        # A0:9E:1A:5E:EF:F6 represents MAC Address of Polar H7 device
        os.system("gatttool -b A0:9E:1A:5E:EF:F6 --char-write-req --handle=0x0013 --value=0100 --listen > " + out)

    def start_baseline_thread(self):
        Thread(target=self.get_baseline).start()
        self.baseline_button.text == "..."



    def main_screen(self):
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def get_baseline(self):
        global baseline_1

        output_filename = "hr_output_" + str(datetime.now().strftime("%m-%d-%Y")) + ".txt"
        bt_thread = Thread(target=lambda: self.read_btle(output_filename))
        bt_thread.daemon = True
        bt_thread.start()
        sleep(4)

        with open(output_filename, "r") as logfile:
            loglines = self.follow(logfile)
            count = 0
            baseline = 0
            heart_rate = []

            for line in loglines:
                hr_in_hex = line[39:41]


                if count != 10 and baseline == 0:
                    heart_rate.append(int(hr_in_hex, 16))
                    print(heart_rate[count])
                    count += 1
                    self.baseline_button.text = "." * ((count%3) + 1)
                    sleep(0.5)

                elif count == 10 and baseline == 0:
                    print("Getting average...")
                    self.baseline_button.text = "Get Baseline"
                    baseline_1 = self.get_avg(heart_rate)
                    baseline += 1
                    heart_rate.clear()
                    count = 0
                    self.check = 1
                    self.enable_buttons()
                    print("Baseline is:", )



    def prepare_race(self):
        ax.set_vel(0)
        self.disable_buttons()
        ax.set_vel(1)
        while ax.is_busy():
            sleep(1)
        ax.set_vel(0)
        ax.set_vel_limit(5)
        ax.set_pos_traj((ax.get_pos() - 0.5), 0.5, 1, 0.5)
        while ax.is_busy():
            sleep(0.5)
        ax.set_home()
        if self.check == 1:
            self.enable_buttons()
        sleep(1)

    def get_avg(self,heart_rate):
        print("Getting baseline...")
        total = 0
        for element in heart_rate:
            total += element

        avg = total / len(heart_rate)
        return avg

    def run_chaos_thread(self):
        self.prepare_race
        self.counter_screen()
        Thread(target=self.run_chaos_setting).start()

    def run_chaos_setting(self):
        SCREEN_MANAGER.current = CHAOS_SCREEN_NAME

    def run_steady_thread(self):
        self.run_steady_setting()
        Thread(target=self.run_steady_setting).start()

    def run_steady_setting(self):
        SCREEN_MANAGER.current = STEADY_SCREEN_NAME

    def run_zen_thread(self):
        self.counter_screen()
        Thread(target=self.run_zen_setting).start()

    def run_zen_setting(self):
        SCREEN_MANAGER.current = ZEN_SCREEN_NAME


    def test_motor_screen(self):
        SCREEN_MANAGER.current = TEST_SCREEN_NAME


class SteadyScreen(Screen):

    text_button = ObjectProperty(None)
    back_button = ObjectProperty(None)

    count = 0
    i = 5

    def sensor_check(self):
        while self.check_gpio() == False:
            sleep(0.01)
        print("You won!")
        sleep(5)
        self.game_screen()

    def check_gpio(self):
        if od.get_gpio_states() & 0b100 == 0:
            return True
        else:
            return False

    def read_btle(self, out):
        # A0:9E:1A:5E:EF:F6 represents MAC Address of Polar H7 device
        os.system("gatttool -b A0:9E:1A:5E:EF:F6 --char-write-req --handle=0x0013 --value=0100 --listen > " + out)

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

    def get_diff(self, heart_rate, baseline):
        max = heart_rate[0]

        for element in heart_rate:
            if element > max:
                max = element
        diff = max - baseline
        print("Max is:", max)
        print("Baseline is:", baseline_1)
        print("Difference is:", diff)
        return diff

    def start_steady_thread(self):
        Thread(target=self.countdown).start()
        Thread(target=self.sensor_check).start()

    def countdown(self):
        sleep(1)
        while self.i > 0:
            self.i -= 1
            sleep(1)
            self.text_button.text = str(self.i)

        output_filename = "hr_output_" + str(datetime.now().strftime("%m-%d-%Y")) + ".txt"
        bt_thread = Thread(target=lambda: self.read_btle(output_filename))
        bt_thread.daemon = True
        bt_thread.start()


        with open(output_filename, "r") as logfile:
            loglines = self.follow(logfile)
            count = 0
            heart_rate = []

            for line in loglines:
                hr_in_hex = line[39:41]


                if count != 5:

                    heart_rate.append(int(hr_in_hex, 16))
                    self.text_button.text = str(heart_rate[count])
                    count += 1
                    sleep(0.25)

                elif count == 5:

                    diff = self.get_diff(heart_rate, baseline_1)
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

    def game_screen(self):
        SCREEN_MANAGER.current = GAME_SCREEN_NAME


    def steady_setting(self):
        self.start_steady_thread()


    def enable_back_button(self):
        self.back_button.disabled = False

    def disable_back_button(self):
        self.back_button.disabled = True






class ZenScreen(Screen):
    pass



class ChaosScreen(Screen):
    pass




class TestScreen(Screen):
    back_button_3 = ObjectProperty(None)
    motor_speed = ObjectProperty(None)
    count_slider = ObjectProperty(None)
    test_button = ObjectProperty(None)

    def main_screen(self):
        SCREEN_MANAGER.current = GAME_SCREEN_NAME

    def test_motor(self):
        i = 0
        while i < self.count_slider.value:
            ax.set_vel_limit(5)
            ax.set_pos_traj(-8,self.motor_speed.value/10,self.motor_speed.value/5,self.motor_speed.value/10)
            while ax.is_busy():
                sleep(5)
            ax.set_pos_traj(0,self.motor_speed.value/10,self.motor_speed.value/5,self.motor_speed.value/10)
            while ax.is_busy():
                sleep(5)
            i+=1


Builder.load_file('main.kv')
Builder.load_file('GameScreen.kv')
Builder.load_file('InstructionsScreen.kv')
Builder.load_file('CounterScreen.kv')
Builder.load_file('TestScreen.kv')
Builder.load_file('SteadyScreen.kv')
Builder.load_file('ZenScreen.kv')
Builder.load_file('ChaosScreen.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(InstructionsScreen(name=INSTRUCTIONS_SCREEN_NAME))
SCREEN_MANAGER.add_widget(GameScreen(name=GAME_SCREEN_NAME))
SCREEN_MANAGER.add_widget(TestScreen(name=TEST_SCREEN_NAME))
SCREEN_MANAGER.add_widget(SteadyScreen(name=STEADY_SCREEN_NAME))
SCREEN_MANAGER.add_widget(ChaosScreen(name=CHAOS_SCREEN_NAME))


def send_event(event_name):
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()

if __name__ == '__main__':
    MainApp().run()