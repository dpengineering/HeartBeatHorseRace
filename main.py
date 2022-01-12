import sys
import time
import threading
import pygatt
from binascii import hexlify
import time

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
current_heartrate = 0
race_finished = False

adapter0 = pygatt.BGAPIBackend()


# adapter1 = pygatt.GATTToolBackend()


def handle_data(handle, value):
    global current_heartrate
    current_heartrate = (int(hexlify(value)[2:4], 16))
    #print("Player Heart Rate: %s" % (int(hexlify(value)[2:4], 16)))

adapter0.start()
# adapter1.start()
# chest_polar = adapter0.connect("A0:9E:1A:49:A8:51")
hand_polar = adapter0.connect("A0:9E:1A:5E:EF:F6")

# chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(0))

hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data)


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

    global race_finished
    global current_heartrate

    check = 0

    back_button_2 = ObjectProperty(None)
    baseline_button = ObjectProperty(None)
    steady_button = ObjectProperty(None)
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
        self.steady_button.disabled = False
        self.chaos_button.disabled = False
        self.zen_button.disabled = False

    def disable_buttons(self):
        self.steady_button.disabled = True
        self.chaos_button.disabled = True
        self.zen_button.disabled = True

    def start_baseline_thread(self):
        Thread(target=self.get_baseline).start()
        self.baseline_button.text == "..."



    def main_screen(self):
        SCREEN_MANAGER.current = MAIN_SCREEN_NAME

    def get_baseline(self):
        global baseline_1
        global current_heartrate

        count = 0
        heart_rate = []

        while count != 10:
            heart_rate.append(current_heartrate)
            print(heart_rate[count])
            count += 1
            self.baseline_button.text = "." * ((count%3) + 1)
            sleep(0.5)

        print("Getting average...")
        self.baseline_button.text = "Get Baseline"
        baseline_1 = self.get_avg(heart_rate)
        heart_rate.clear()
        count = 0
        self.check = 1
        # Used to check if there is baseline heart rate when preparing race
        self.enable_buttons()
        print("Baseline is:", )



    def prepare_race(self):
        race_finished = False
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


class ChaosScreen(Screen):

    global race_finished
    global current_heartrate

    text_button = ObjectProperty(None)
    back_button = ObjectProperty(None)

    count = 0
    i = 5

    def sensor_check(self):
        while self.check_gpio() == False:
            sleep(0.01)
        print("You won!")
        race_finished = True
        sleep(5)
        self.enable_back_button()
        self.game_screen()

    def check_gpio(self):
        if od.get_gpio_states() & 0b100 == 0:
            return True
        else:
            return False


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

    def start_chaos_thread(self):
        Thread(target=self.countdown).start()
        Thread(target=self.sensor_check).start()

    def countdown(self):
        self.i = 5
        self.text_button.text = str(self.i)
        self.disable_back_button()
        sleep(1)
        while self.i > 0:
            # Countdown loop
            self.i -= 1
            sleep(1)
            self.text_button.text = str(self.i)

            if count != 5:

                heart_rate.append(self.current_heartrate)
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


    def chaos_setting(self):
        self.start_chaos_thread()

    def enable_back_button(self):
        self.back_button.disabled = False

    def disable_back_button(self):
        self.back_button.disabled = True






class ZenScreen(Screen):

    global race_finished
    global current_heartrate

    text_button = ObjectProperty(None)
    back_button = ObjectProperty(None)

    count = 0
    i = 5

    def sensor_check(self):
        while self.check_gpio() == False:
            sleep(0.01)
        print("You won!")
        race_finished = True
        sleep(5)
        self.enable_back_button()
        self.game_screen()

    def check_gpio(self):
        if od.get_gpio_states() & 0b100 == 0:
            return True
        else:
            return False

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

    def start_zen_thread(self):
        Thread(target=self.countdown).start()
        Thread(target=self.sensor_check).start()

    def countdown(self):
        self.i = 5
        self.text_button.text = str(self.i)
        self.disable_back_button()
        sleep(1)
        while self.i > 0:
            self.i -= 1
            sleep(1)
            self.text_button.text = str(self.i)

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


    def zen_setting(self):
        self.start_chaos_thread()

    def enable_back_button(self):
        self.back_button.disabled = False

    def disable_back_button(self):
        self.back_button.disabled = True



class SteadyScreen(Screen):
    pass




class TestScreen(Screen):
    back_button_3 = ObjectProperty(None)
    motor_speed = ObjectProperty(None)
    count_slider = ObjectProperty(None)
    test_button = ObjectProperty(None)
    testindefinitely_button = ObjectProperty(None)

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

    def test_indefinitely(self):
        while True:
            ax.set_vel_limit(5)
            ax.set_pos_traj(-8, self.motor_speed.value / 10, self.motor_speed.value / 5, self.motor_speed.value / 10)
            while ax.is_busy():
                sleep(5)
            ax.set_pos_traj(0, self.motor_speed.value / 10, self.motor_speed.value / 5, self.motor_speed.value / 10)
            while ax.is_busy():
                sleep(5)


Builder.load_file('main.kv')
Builder.load_file('GameScreen.kv')
Builder.load_file('InstructionsScreen.kv')
Builder.load_file('CounterScreen.kv')
Builder.load_file('TestScreen.kv')
Builder.load_file('ChaosScreen.kv')
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