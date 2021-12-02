import sys
import time
import threading

import os
os.environ['DISPLAY'] = ":0.0"
os.environ['KIVY_WINDOW'] = 'sdl2'

from RPi_ODrive import ODrive_Ease_Lib
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

od = odrive.find_any()
ax = ODrive_Ease_Lib.ODrive_Axis(od.axis0)

MIXPANEL_TOKEN = "x"
MIXPANEL = MixPanel("Project Name", MIXPANEL_TOKEN)

SCREEN_MANAGER = ScreenManager()
MAIN_SCREEN_NAME = 'main'
GAME_SCREEN_NAME = 'game'
COUNTER_SCREEN_NAME = 'counter'
INSTRUCTIONS_SCREEN_NAME = 'instructions'
TEST_SCREEN_NAME = 'test'

class MainApp(App):

    def build(self):
        return SCREEN_MANAGER




class MainScreen(Screen):

    instructions_button = ObjectProperty(None)
    continue_button = ObjectProperty(None)

    def instructions_screen(self):
        SCREEN_MANAGER.current = INSTRUCTIONS_SCREEN_NAME

    def game_screen(self):
        SCREEN_MANAGER.current = GAME_SCREEN_NAME




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
        output_filename = "hr_output_" + str(datetime.now().strftime("%m-%d-%Y")) + ".txt"
        bt_thread = Thread(target=lambda: self.read_btle(output_filename))
        bt_thread.daemon = True
        bt_thread.start()
        sleep(3)

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
                    avg = self.get_avg(heart_rate)
                    baseline += 1
                    heart_rate.clear()
                    count = 0
                    self.check = 1
                    self.enable_buttons()



    def prepare_race(self):
        self.disable_buttons()
        ax.finished = False
        ax.set_vel(1)
        while ax.is_busy():
            sleep(1)
        ax.set_vel(0)
        ax.set_vel_limit(0.5)
        ax.set_pos(ax.get_pos() - 0.5)
        while ax.is_busy():
            sleep(0.5)
        ax.set_vel_limit(5)
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
        if self.baseline == False:
            pass
        self.prepare_race
        self.counter_screen()
        Thread(target=self.run_chaos_setting).start()

    def run_chaos_setting(self):
        pass

    def run_steady_thread(self):
        if self.baseline == False:
            pass
        self.counter_screen()
        Thread(target=self.run_zen_setting).start()

    def run_zen_thread(self):
        self.counter_screen()
        Thread(target=self.run_steady_setting).start()

    def counter_screen(self):
        SCREEN_MANAGER.current = COUNTER_SCREEN_NAME

    def test_motor_screen(self):
        SCREEN_MANAGER.current = TEST_SCREEN_NAME



class TestScreen(Screen):
    back_button_3 = ObjectProperty(None)

    def back_to_mainscreen(self):
        SCREEN_MANAGER.current = GAME_SCREEN_NAME


class CounterScreen(Screen):
    pass


Builder.load_file('main.kv')
Builder.load_file('GameScreen.kv')
Builder.load_file('InstructionsScreen.kv')
Builder.load_file('CounterScreen.kv')
Builder.load_file('TestScreen.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(InstructionsScreen(name=INSTRUCTIONS_SCREEN_NAME))
SCREEN_MANAGER.add_widget(GameScreen(name=GAME_SCREEN_NAME))
SCREEN_MANAGER.add_widget(CounterScreen(name=COUNTER_SCREEN_NAME))
SCREEN_MANAGER.add_widget(TestScreen(name=TEST_SCREEN_NAME))


def send_event(event_name):
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()

if __name__ == '__main__':
    MainApp().run()