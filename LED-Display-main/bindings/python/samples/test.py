import time
from time import sleep, clock
import multiprocessing
import rgbmatrix
from rgbmatrix.core import RGBMatrix, RGBMatrixOptions
from samplebase import SampleBase
from rgbmatrix import graphics
from pidev.Joystick import Joystick
import sys
from PIL import Image
import os
import board
import busio
import adafruit_vl6180x

os.environ['DISPLAY'] = ":0.0"
#os.environ['KIVY_WINDOW'] = 'egl_rpi'

class Test(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        # self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello World!")

    def run(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_vl6180x.VL6180X(i2c)
        self.joy = Joystick(0, False)
        self.board = self.matrix.CreateFrameCanvas()
        self.font1 = graphics.Font()
        self.font1.LoadFont("../../../fonts/8x13B.bdf")
        self.font2 = graphics.Font()
        self.font2.LoadFont("../../../fonts/8x13B.bdf")
        self.font3 = graphics.Font()
        self.font3.LoadFont("../../../fonts/10x20.bdf")
        self.font4 = graphics.Font()
        self.font4.LoadFont("../../../fonts/retro-gaming7.bdf")
        self.font5 = graphics.Font()
        self.font5.LoadFont("../../../fonts/retro-gaming-big3.bdf")
        self.font6 = graphics.Font()
        self.font6.LoadFont("../../../fonts/6x10.bdf")
        self.font7 = graphics.Font()
        self.font7.LoadFont("../../../fonts/retro-gaming3.bdf")
        self.text_color1 = graphics.Color(0, 255, 0)
        self.pos1 = self.board.width
        self.my_text1 = "Your"
        self.text_color2 = graphics.Color(0, 0, 255)
        self.pos2 = -50
        self.my_text2 = "Score"
        self.text_color3 = graphics.Color(255, 255, 255)
        self.pos3 = 100
        self.my_text3 = "50"
        self.text_color4 = graphics.Color(255, 0, 0)
        self.pos4 = 40
        # Thread(target=self.your_score_screen).start()
        # Thread(target=self.high_score_list).start()
        # Thread(target=self.keyboard).start()
        # Thread(target=self.screensaver).start()
        # Thread(target=self.image).start()
        # Thread(target=self.high).start()
        # Thread(target=self.score).start()
        # self.screensaver_thread = multiprocessing.Process(target=self.screensaver)
        # self.your_score_screen_thread = multiprocessing.Process(target=self.your_score_screen)
        # self.high_score_list_thread = multiprocessing.Process(target=self.high_score_list)
        # self.keyboard_thread = multiprocessing.Process(target=self.keyboard)
        # self.screensaver_thread.start()
        self.screensaver()

    def timer(self):
        start = time.time()
        while 0 <= int(time.time()-start) < 10:
            if int(self.sensor.range) < 255:
                break
            # if self.joy.get_button_state(0) == True:
            #     while self.joy.get_button_state(0) == True:
            #         sleep(0.1)
            #     break
            self.board.Clear()
            graphics.DrawText(self.board, self.font5, 53, 27, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 51, 27, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 52, 28, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 52, 26, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 52, 27, self.text_color4, str(int(time.time() - start)))
            self.board = self.matrix.SwapOnVSync(self.board)
            sleep(0.1)
        while 10 <= int(time.time()-start) < 20:
            if int(self.sensor.range) < 255:
                break
            # if self.joy.get_button_state(0) == True:
            #     while self.joy.get_button_state(0) == True:
            #         sleep(0.1)
            #     break
            self.board.Clear()
            graphics.DrawText(self.board, self.font5, 46, 27, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 44, 27, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 45, 28, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 45, 26, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 45, 27, self.text_color4, str(int(time.time()-start)))
            self.board = self.matrix.SwapOnVSync(self.board)
            sleep(0.1)
        while 20 <= int(time.time()-start) < 100:
            if int(self.sensor.range) < 255:
                break
            # if self.joy.get_button_state(0) == True:
            #     while self.joy.get_button_state(0) == True:
            #         sleep(0.1)
            #     break
            self.board.Clear()
            graphics.DrawText(self.board, self.font5, 42, 27, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 40, 27, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 41, 28, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 41, 26, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 41, 27, self.text_color4, str(int(time.time()-start)))
            self.board = self.matrix.SwapOnVSync(self.board)
            sleep(0.1)
        while 100 <= int(time.time()-start) < 110:
            if int(self.sensor.range) < 255:
                break
            # if self.joy.get_button_state(0) == True:
            #     while self.joy.get_button_state(0) == True:
            #         sleep(0.1)
            #     break
            self.board.Clear()
            graphics.DrawText(self.board, self.font5, 35, 27, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 33, 27, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 34, 28, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 34, 26, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 34, 27, self.text_color4, str(int(time.time()-start)))
            self.board = self.matrix.SwapOnVSync(self.board)
            sleep(0.1)
        while 110 <= int(time.time()-start) < 200:
            if int(self.sensor.range) < 255:
                break
            # if self.joy.get_button_state(0) == True:
            #     while self.joy.get_button_state(0) == True:
            #         sleep(0.1)
            #     break
            self.board.Clear()
            graphics.DrawText(self.board, self.font5, 39, 27, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 37, 27, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 38, 28, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 38, 26, self.text_color3, str(int(time.time() - start)))
            graphics.DrawText(self.board, self.font5, 38, 27, self.text_color4, str(int(time.time()-start)))
            self.board = self.matrix.SwapOnVSync(self.board)
            sleep(0.1)
        while 200 <= int(time.time()-start) < 999:
            if int(self.sensor.range) < 255:
                break
            # if self.joy.get_button_state(0) == True:
            #     while self.joy.get_button_state(0) == True:
            #         sleep(0.1)
            #     break
            self.board.Clear()
            graphics.DrawText(self.board, self.font5, 30, 27, self.text_color3, str(int(time.time()-start)))
            self.board = self.matrix.SwapOnVSync(self.board)
            sleep(0.1)
        while int(time.time()-start) > 999:
            self.board.Clear()
            graphics.DrawText(self.board, self.font5, 30, 27, self.text_color3, "999")
            self.board = self.matrix.SwapOnVSync(self.board)
            sleep(0.1)
            if int(self.sensor.range) < 255:
                break
            # if self.joy.get_button_state(0) == True:
            #     while self.joy.get_button_state(0) == True:
            #         sleep(0.1)
            #     break
        self.score = int((time.time() - start))
        if self.score > 999:
            self.score = 999
        self.keyboard()

    def sort(self):
        scores = []
        names = []
        with open("scores.txt", "r") as file:
            for line in file:
                split_line = line.strip().split()
                if split_line != []:
                    names.append(split_line[0])
                    scores.append(split_line[1])
            pairs = list(zip(scores, names))
            if pairs != []:
                pairs.sort(key=lambda pair: int(pair[0]))
        with open("scores.txt", "w") as file:
            for p in pairs:
                score, name = p
                file.write(name+" "+score+"\n")

    def high_score_list(self):
        self.sort()
        with open("scores.txt") as file:
            lines = file.readlines()
            lines = [line.rstrip() for line in lines]
        offset = 15
        starting_pos = 40
        x_pos = 29
        y_pos = 10
        counter = 0
        pos = self.board.width
        start = time.time()
        while int(time.time() - start) <= 30:
            if self.joy.get_button_state(0) == True:
                while self.joy.get_button_state(0) == True:
                    sleep(0.1)
                break
            self.board.Clear()
            if counter%2 == 0:
                self.pos4 -= 1
            i = 0
            for num,name in enumerate(lines):
                i += 1
                if self.pos4 <= starting_pos-num*offset:
                    graphics.DrawText(self.board, self.font4, x_pos, self.pos4+num*offset, self.text_color3, str(num+1)+". "+name)
            if self.pos4 + len(lines)*offset < 0:
                self.pos4 = starting_pos
            for x in range(128):
                for y in range(11):
                    self.board.SetPixel(x, y, 0, 0, 0)
            length = graphics.DrawText(self.board, self.font4, pos, y_pos, self.text_color4, "HIGH SCORES")
            graphics.DrawText(self.board, self.font4, pos-1, y_pos-1, self.text_color3, "HIGH SCORES")
            pos -= 1
            if (pos + length < 0):
                pos = self.board.width
            self.board = self.matrix.SwapOnVSync(self.board)
            sleep(0.025)
            counter += 1
        self.board.Clear()
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(1.5)
        self.screensaver()

    def start_screen(self):
        self.board.Clear()
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(3)
        position1 = -5
        position2 = 60
        while True:
            self.board.Clear()
            graphics.DrawText(self.board, self.font1, 4, position1, self.text_color3, "READY")
            graphics.DrawText(self.board, self.font1, 2, position1, self.text_color3, "READY")
            graphics.DrawText(self.board, self.font1, 3, position1+1, self.text_color3, "READY")
            graphics.DrawText(self.board, self.font1, 3, position1-1, self.text_color3, "READY")
            graphics.DrawText(self.board, self.font1, 3, position1, self.text_color4, "READY")
            graphics.DrawText(self.board, self.font2, 103, position2, self.text_color3, "SET")
            graphics.DrawText(self.board, self.font2, 101, position2, self.text_color3, "SET")
            graphics.DrawText(self.board, self.font2, 102, position2+1, self.text_color3, "SET")
            graphics.DrawText(self.board, self.font2, 102, position2-1, self.text_color3, "SET")
            graphics.DrawText(self.board, self.font2, 102, position2, self.text_color4, "SET")
            if position2 == 20:
                break
            if position1 != 20:
                position1 += 1
                sleep(0.025)
            else:
                position2 -= 1
                sleep(0.025)
            self.board = self.matrix.SwapOnVSync(self.board)
        self.board.Clear()
        graphics.DrawText(self.board, self.font1, 4, position1, self.text_color3, "READY")
        graphics.DrawText(self.board, self.font1, 2, position1, self.text_color3, "READY")
        graphics.DrawText(self.board, self.font1, 3, position1 + 1, self.text_color3, "READY")
        graphics.DrawText(self.board, self.font1, 3, position1 - 1, self.text_color3, "READY")
        graphics.DrawText(self.board, self.font1, 3, position1, self.text_color4, "READY")
        graphics.DrawText(self.board, self.font2, 103, position2, self.text_color3, "SET")
        graphics.DrawText(self.board, self.font2, 101, position2, self.text_color3, "SET")
        graphics.DrawText(self.board, self.font2, 102, position2 + 1, self.text_color3, "SET")
        graphics.DrawText(self.board, self.font2, 102, position2 - 1, self.text_color3, "SET")
        graphics.DrawText(self.board, self.font2, 102, position2, self.text_color4, "SET")
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(1)
        for x in range(200):
            for y in range(200):
                self.board.SetPixel(x, y, 0, 0, 0)
        graphics.DrawText(self.board, self.font5, 39, 27, self.text_color3, "GO!")
        graphics.DrawText(self.board, self.font5, 37, 27, self.text_color3, "GO!")
        graphics.DrawText(self.board, self.font5, 38, 26, self.text_color3, "GO!")
        graphics.DrawText(self.board, self.font5, 38, 28, self.text_color3, "GO!")
        graphics.DrawText(self.board, self.font5, 38, 27, self.text_color4, "GO!")
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(3)
        self.timer()

    def keyboard(self):
        sleep(1)
        i = 0
        j = 0
        k = 0
        r = 255
        g = 0
        b = 0
        width = 7
        height = 7
        name = ""
        letter_list = ["A B C D E F G H I J", "K L M N O P Q R S T", "U V W X Y Z. DEL OK"]
        current_row = 0
        while True:
            self.board.Clear()
            for x in range(width):
                self.board.SetPixel(6 + x + i, 2 + j, r, g, b)
                self.board.SetPixel(6 + x + i, 10 + j, r, g, b)
            for x in range(height):
                self.board.SetPixel(12 + i + k, 10 - (x + 1) + j, r, g, b)
                self.board.SetPixel(6 + i, 10 - (x + 1) + j, r, g, b)
            self.board.SetPixel(38, 19, 255, 0, 0)
            self.board.SetPixel(38, 20, 255, 0, 0)
            self.board.SetPixel(39, 19, 255, 0, 0)
            self.board.SetPixel(39, 20, 255, 0, 0)
            self.board.SetPixel(38, 22, 255, 0, 0)
            self.board.SetPixel(38, 23, 255, 0, 0)
            self.board.SetPixel(39, 22, 255, 0, 0)
            self.board.SetPixel(39, 23, 255, 0, 0)
            self.board.SetPixel(99, 19, 255, 0, 0)
            self.board.SetPixel(99, 20, 255, 0, 0)
            self.board.SetPixel(100, 19, 255, 0, 0)
            self.board.SetPixel(100, 20, 255, 0, 0)
            self.board.SetPixel(99, 22, 255, 0, 0)
            self.board.SetPixel(99, 23, 255, 0, 0)
            self.board.SetPixel(100, 22, 255, 0, 0)
            self.board.SetPixel(100, 23, 255, 0, 0)
            graphics.DrawText(self.board, self.font6, 7, 10, self.text_color3, letter_list[current_row])
            graphics.DrawText(self.board, self.font6, 7, 25, graphics.Color(255, 0, 0), "SCORE ")
            graphics.DrawText(self.board, self.font6, 42, 25, graphics.Color(255, 255, 255), str(self.score))
            graphics.DrawText(self.board, self.font6, 74, 25, graphics.Color(255, 0, 0), "NAME ")
            graphics.DrawText(self.board, self.font6, 103, 25, graphics.Color(255, 255, 255), name)
            self.board.SetPixel(75, 10, 0, 0, 0)
            self.board.SetPixel(75, 9, 0, 0, 0)
            self.board.SetPixel(75, 8, 0, 0, 0)
            self.board.SetPixel(74, 9, 0, 0, 0)
            self.board.SetPixel(76, 9, 0, 0, 0)
            # self.board = self.matrix.SwapOnVSync(self.board)
            row, column = current_row, int((6+x+i)/12)
            if i == 72 and row == 1:
                self.board.SetPixel(78, 10, 255, 0, 0)
                self.board.SetPixel(78, 11, 255, 0, 0)
                self.board.SetPixel(79, 11, 255, 0, 0)
                self.board.SetPixel(80, 11, 255, 0, 0)
                self.board.SetPixel(81, 11, 255, 0, 0)
                self.board.SetPixel(82, 11, 255, 0, 0)
                self.board.SetPixel(83, 11, 255, 0, 0)
                self.board.SetPixel(84, 11, 255, 0, 0)
                self.board.SetPixel(84, 10, 255, 0, 0)
                self.board.SetPixel(79, 10, 0, 0, 0)
                self.board.SetPixel(80, 10, 0, 0, 0)
                self.board.SetPixel(81, 10, 0, 0, 0)
                self.board.SetPixel(82, 10, 0, 0, 0)
            if self.joy.get_button_state(4) == True:
                while self.joy.get_button_state(4) == True:
                    sleep(0.1)
                # self.board.Clear()
                # print("+1",letter_list[row].split()[column+1])
                # print("normal",letter_list[row].split()[column])
                # print(i, row)
                if row == 2 and i > 78:
                    i = -12
                    r = 255
                    g = 0
                    width = 7
                    height = 7
                    k = 0
                elif 6+x+i >= 118:
                    i = -12
                elif letter_list[row].split()[column] == "DEL":
                    i += 6
                    width = 19
                    k = 12
                elif letter_list[row].split()[column] == "OK":
                    r = 0
                    g = 255
                    i += 12
                    width = 13
                    k = 6
                i += 12
            if self.joy.get_button_state(3) == True:
                while self.joy.get_button_state(3) == True:
                    sleep(0.1)
                # self.board.Clear()
                # print(i)
                # print("normal", letter_list[row].split()[column-2])
                if row == 2 and i < 12:
                    i = 114
                    r = 0
                    g = 255
                    width = 13
                    k = 6
                elif 6+x+i <= 12:
                    i = 120
                elif row == 2 and i == 102:
                    i -= 12
                    width = 19
                    k = 12
                    r = 255
                    g = 0
                elif letter_list[row].split()[column-2] == "Z.":
                    i -= 6
                    r = 255
                    g = 0
                    width = 7
                    height = 7
                    k = 0
                i -= 12
            if self.joy.get_button_state(2) == True:
                # # self.board.Clear()
                # j -= 10
                # if 10-(x+1)+j <= 2:
                #     j = 20
                while self.joy.get_button_state(2) == True:
                    sleep(0.1)
                if g == 255:
                    i = 96
                    r = 255
                    g = 0
                    width = 7
                    height = 7
                    k = 0
                elif letter_list[row].split()[column-1] == "G" or letter_list[row].split()[column-1] == "H":#i == 72 or i == 84 and row == 1:
                    i = 78
                    width = 19
                    k = 12
                    r = 255
                    g = 0
                elif letter_list[row].split()[column-1] == "I" or letter_list[row].split()[column-1] == "J":#i == 96 or i == 108 and row == 1:
                    i = 102
                    r = 0
                    g = 255
                    width = 13
                    k = 6
                elif letter_list[row].split()[column-1] == "DEL":
                    i = 72
                    r = 255
                    g = 0
                    width = 7
                    height = 7
                    k = 0
                current_row -= 1
                current_row %= len(letter_list)
                # if i >= 60 and row == 0:
                #     i = 60
            if self.joy.get_button_state(1) == True:
                # # self.board.Clear()
                # j += 10
                # if 10-(x+1)+j >= 32:
                #     j = 0
                while self.joy.get_button_state(1) == True:
                    sleep(0.1)
                if g == 255:
                    i = 96
                    r = 255
                    g = 0
                    width = 7
                    height = 7
                    k = 0
                elif letter_list[row].split()[column-1] == "Q" or letter_list[row].split()[column-1] == "R":#i == 72 or i == 84 and row == 1:
                    i = 78
                    width = 19
                    k = 12
                    r = 255
                    g = 0
                elif letter_list[row].split()[column-1] == "S" or letter_list[row].split()[column-1] == "T":#i == 96 or i == 108 and row == 1:
                    i = 102
                    r = 0
                    g = 255
                    width = 13
                    k = 6
                elif letter_list[row].split()[column-1] == "DEL":
                    i = 72
                    r = 255
                    g = 0
                    width = 7
                    height = 7
                    k = 0
                current_row += 1
                current_row %= len(letter_list)
                # if i >= 60 and row == 1:
                #     i = 60
            if self.joy.get_button_state(0) == True:
                while self.joy.get_button_state(0) == True:
                    sleep(0.1)
                if row == 2 and i == 102 and len(name) == 0:
                    easter_egg = "GO PACK GO!"
                elif row == 2 and i == 102:
                    with open("scores.txt", "a") as file:
                        file.write(name + " " + str(self.score) + "\n")
                    self.high_score_list()
                elif row == 2 and i == 78:
                    name = name[0:len(name)-1]
                elif len(name) >= 3:
                    easter_egg = "NFC 1st SEED 2021-22"
                elif letter_list[row].split()[column-1] == "Z.":
                    name += "Z"
                else:
                    name += letter_list[row].split()[column-1]
            self.board = self.matrix.SwapOnVSync(self.board)


    def screensaver(self):
        pos = self.board.width
        while True:
            self.board.Clear()
            graphics.DrawText(self.board, self.font7, 55, 31, self.text_color3, "PLAY")
            graphics.DrawText(self.board, self.font5, pos-1, 23, self.text_color3, "TIPPY MAZE")
            graphics.DrawText(self.board, self.font5, pos+1, 23, self.text_color3, "TIPPY MAZE")
            graphics.DrawText(self.board, self.font5, pos, 22, self.text_color3, "TIPPY MAZE")
            graphics.DrawText(self.board, self.font5, pos, 24, self.text_color3, "TIPPY MAZE")
            length = graphics.DrawText(self.board, self.font5, pos, 23, self.text_color4, "TIPPY MAZE")
            pos -= 1
            sleep(0.03)
            if (pos + length < 0):
                pos = self.board.width
            self.board = self.matrix.SwapOnVSync(self.board)
            if self.joy.get_button_state(0) == True:
                while self.joy.get_button_state(0) == True:
                    sleep(0.1)
                    graphics.DrawText(self.board, self.font7, 55, 31, self.text_color4, "PLAY")
                    self.board = self.matrix.SwapOnVSync(self.board)
                graphics.DrawText(self.board, self.font7, 55, 31, self.text_color3, "PLAY")
                self.board = self.matrix.SwapOnVSync(self.board)
                sleep(1)
                self.start_screen()

# Main function
if __name__ == "__main__":
    test = Test()
    if (not test.process()):
        test.print_help()
