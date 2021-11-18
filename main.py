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

    baseline = False

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

        self.baseline = True

    def prepare_race(self):
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
        sleep(1)


    def run_chaos_thread(self):
        if self.baseline == False:
            pass
        self.prepare_race
        self.counter_screen()
        Thread(target=self.run_chaos_setting).start()

    def run_chaos_setting(self):


    def run_steady_thread(self):
        if self.baseline == False:
            pass
        self.counter_screen()
        Thread(target=self.run_zen_setting).start()

    def run_zen_thread(self):
        if self.baseline == False:
            pass
        self.counter_screen()
        Thread(target=self.run_steady_setting).start()

    def counter_screen(self):
        SCREEN_MANAGER.current = COUNTER_SCREEN_NAME




class CounterScreen(Screen):



Builder.load_file('main.kv')
Builder.load_file('GameScreen.kv')
Builder.load_file('InstructionsScreen.kv')
Builder.load_file('CounterScreen.kv')
SCREEN_MANAGER.add_widget(MainScreen(name=MAIN_SCREEN_NAME))
SCREEN_MANAGER.add_widget(InstructionsScreen(name=INSTRUCTIONS_SCREEN_NAME))
SCREEN_MANAGER.add_widget(GameScreen(name=GAME_SCREEN_NAME))
SCREEN_MANAGER.add_widget(CounterScreen(name=COUNTER_SCREEN_NAME))


def send_event(event_name):
    global MIXPANEL

    MIXPANEL.set_event_name(event_name)
    MIXPANEL.send_event()

if __name__ == '__main__':
    MainApp().run()