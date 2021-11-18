import sys
import time
import threading
from time import sleep
from datetime import datetime
from threading import Thread
from RPi_ODrive import ODrive_Ease_Lib
import odrive

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

def get_avg(self, heart_rate):
    print("Getting baseline...")
    total = 0
    for element in heart_rate:
        total += element

    avg = total / len(heart_rate)
    return avg