import time
from time import sleep
from samplebase import SampleBase
from rgbmatrix import graphics
import os
import board
import busio
import adafruit_vl6180x
import enum
from p2p.dpea_p2p import Client
from threading import Thread

os.environ['DISPLAY'] = ":0.0"

class PacketType(enum.Enum):
    NULL = 0
    COMMAND1 = 1
    COMMAND2 = 2

#          |Server IP           |Port |Packet enum
c = Client("172.17.21.47", 5001, PacketType)

joyvalue = None

class Matrix(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Matrix, self).__init__(*args, **kwargs)

    def run(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_vl6180x.VL6180X(i2c)
        self.board = self.matrix.CreateFrameCanvas()
        self.font2 = graphics.Font()
        self.font2.LoadFont("/home/pi/Documents/TippyMaze/matrix/fonts/8x13B.bdf")
        self.font4 = graphics.Font()
        self.font4.LoadFont("/home/pi/Documents/TippyMaze/matrix/fonts/retro-gaming7.bdf")
        self.font5 = graphics.Font()
        self.font5.LoadFont("/home/pi/Documents/TippyMaze/matrix/fonts/retro-gaming-big3.bdf")
        self.font6 = graphics.Font()
        self.font6.LoadFont("/home/pi/Documents/TippyMaze/matrix/fonts/6x10.bdf")
        self.font7 = graphics.Font()
        self.font7.LoadFont("/home/pi/Documents/TippyMaze/matrix/fonts/retro-gaming3.bdf")
        self.text_color3 = graphics.Color(255, 255, 255)
        self.text_color4 = graphics.Color(255, 0, 0)
        self.screens = {"screensaver": self.screensaver, "start_screen": self.start_screen, "timer": self.timer,
                        "keyboard": self.keyboard, "high_score_list": self.high_score_list}
        Thread(target=self.joy_listen).start()
        self.screensaver()

    def joy_listen(self):
        global joyvalue
        c.connect()
        while True:
            pack = c.recv_packet()
            joyvalue = pack[1].decode()
            sleep(0.05)

    def timer(self):
        while joyvalue != "15":
            sleep(0.1)
        start = time.time()
        def center_time(x):
            self.board.Clear()
            self.text_with_outline(str(int(time.time()-start)), "white", "red", self.font5, x, 27)
            self.board = self.matrix.SwapOnVSync(self.board)
            sleep(0.1)
        while joyvalue != "17":
            if 0 <= int(time.time()-start) < 10:
                center_time(52)
            elif 10 <= int(time.time()-start) < 20:
                center_time(45)
            elif 20 <= int(time.time()-start) < 100:
                center_time(41)
            elif 100 <= int(time.time()-start) < 110:
                center_time(34)
            elif 110 <= int(time.time()-start) < 200:
                center_time(38)
            elif 200 <= int(time.time()-start) < 999:
                self.board.Clear()
                graphics.DrawText(self.board, self.font5, 30, 27, self.text_color3, str(int(time.time() - start)))
                self.board = self.matrix.SwapOnVSync(self.board)
                sleep(0.1)
            else:
                self.board.Clear()
                graphics.DrawText(self.board, self.font5, 30, 27, self.text_color3, "999")
                self.board = self.matrix.SwapOnVSync(self.board)
                sleep(0.1)
        self.score = int((time.time() - start)) - 1
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
        global joyvalue
        joyvalue = None
        self.pos4 = 40
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
        sleep(0.1)
        while int(time.time() - start) <= 30:
            if joyvalue == "0":
                break
            self.board.Clear()
            if counter%2 == 0:
                self.pos4 -= 1
            i = 0
            for num,name in enumerate(lines):
                i += 1
                if self.pos4 <= starting_pos-num*offset:
                    graphics.DrawText(self.board, self.font4, x_pos, self.pos4 + num * offset, self.text_color3, str(num + 1) + ". " + name)
            if self.pos4 + len(lines)*offset < 0:
                self.pos4 = starting_pos
            for x in range(128):
                for y in range(11):
                    self.board.SetPixel(x, y, 0, 0, 0)
            length = graphics.DrawText(self.board, self.font4, pos, y_pos, self.text_color4, "HIGH SCORES")
            graphics.DrawText(self.board, self.font4, pos - 1, y_pos - 1, self.text_color3, "HIGH SCORES")
            pos -= 1
            if (pos + length < 0):
                pos = self.board.width
            self.board = self.matrix.SwapOnVSync(self.board)
            sleep(0.025)
            counter += 1
        self.board.Clear()
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(1.5)
        return

    def start_screen(self):
        self.board.Clear()
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(3)
        position1 = -5
        position2 = 60
        while True:
            self.board.Clear()
            self.text_with_outline("READY", "white", "red", self.font2, 3, position1)
            self.text_with_outline("SET", "white", "red", self.font2, 102, position2)
            if position2 == 20:
                break
            if position1 != 20:
                position1 += 1
                sleep(0.025)
            else:
                position2 -= 1
                sleep(0.025)
            self.board = self.matrix.SwapOnVSync(self.board)
        sleep(1)
        for x in range(200):
            for y in range(200):
                self.board.SetPixel(x, y, 0, 0, 0)
        self.text_with_outline("GO!", "white", "red", self.font5, 38, 27)
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(2)
        self.timer()

    def keyboard(self):
        global joyvalue
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
            sleep(0.1)
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
            if joyvalue == "4":
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
                joyvalue = None
            if joyvalue == "3":
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
                joyvalue = None
            if joyvalue == "1":
                if g == 255:
                    i = 96
                    r = 255
                    g = 0
                    width = 7
                    height = 7
                    k = 0
                elif letter_list[row].split()[column-1] == "G" or letter_list[row].split()[column-1] == "H":
                    i = 78
                    width = 19
                    k = 12
                    r = 255
                    g = 0
                elif letter_list[row].split()[column-1] == "I" or letter_list[row].split()[column-1] == "J":
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
                joyvalue = None
            if joyvalue == "2":
                if g == 255:
                    i = 96
                    r = 255
                    g = 0
                    width = 7
                    height = 7
                    k = 0
                elif letter_list[row].split()[column-1] == "Q" or letter_list[row].split()[column-1] == "R":
                    i = 78
                    width = 19
                    k = 12
                    r = 255
                    g = 0
                elif letter_list[row].split()[column-1] == "S" or letter_list[row].split()[column-1] == "T":
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
                joyvalue = None
            if joyvalue == "0":
                if row == 2 and i == 102 and len(name) == 0:
                    easter_egg = "GO PACK GO!"
                elif row == 2 and i == 102:
                    with open("scores.txt", "a") as file:
                        file.write(name + " " + str(self.score) + "\n")
                    joyvalue = None
                    self.high_score_list()
                    break
                elif row == 2 and i == 78:
                    name = name[0:len(name)-1]
                elif len(name) >= 3:
                    easter_egg = "NFC 1st SEED 2021-22"
                elif letter_list[row].split()[column-1] == "Z.":
                    name += "Z"
                else:
                    name += letter_list[row].split()[column-1]
                joyvalue = None
            self.board = self.matrix.SwapOnVSync(self.board)

    def screensaver(self):
        global joyvalue
        joyvalue = None
        pos = self.board.width
        length = graphics.DrawText(self.board, self.font5, pos, 23, self.text_color4, "TIPPY MAZE")
        while True:
            self.board.Clear()
            self.text_with_outline("TIPPY MAZE", "white", "red", self.font5, pos, 23)
            pos -= 1
            sleep(0.03)
            if (pos + length < 0):
                pos = self.board.width
            if joyvalue == "7":
                graphics.DrawText(self.board, self.font7, 55, 31, self.text_color4, "PLAY")
            elif joyvalue == "9":
                graphics.DrawText(self.board, self.font7, 55, 31, self.text_color3, "PLAY")
                self.board = self.matrix.SwapOnVSync(self.board)
                joyvalue = None
                sleep(1)
                self.start_screen()
                pos = self.board.width
            else:
                graphics.DrawText(self.board, self.font7, 55, 31, self.text_color3, "PLAY")
            self.board = self.matrix.SwapOnVSync(self.board)

    def draw_text(self, word, outer_color, inner_color, font, x_pos, y_pos):
        while True:
            self.text_with_outline(word, outer_color, inner_color, font, x_pos, y_pos)
            self.board = self.matrix.SwapOnVSync(self.board)

    def horizontal_moving_text(self, word, outer_color, inner_color, font, x_pos, y_pos):
        # x_pos = self.board.width
        length = graphics.DrawText(self.board, font, x_pos, y_pos, self.text_color4, word)
        while True:
            self.board.Clear()
            self.text_with_outline(word, outer_color, inner_color, font, x_pos, y_pos)
            x_pos -= 1
            sleep(0.03)
            if (x_pos + length < 0):
                x_pos = self.board.width
            self.board = self.matrix.SwapOnVSync(self.board)

    def vertical_moving_text(self, word, outer_color, inner_color, font, x_pos, y_pos):
        # y_pos = -5
        while True:
            self.board.Clear()
            self.text_with_outline(word, outer_color, inner_color, font, x_pos, y_pos)
            y_pos += 1
            sleep(0.03)
            if (y_pos > self.board.height+25):
                y_pos = -5
            self.board = self.matrix.SwapOnVSync(self.board)

    def fill_color(self, color):
        if color == "red":
            r = 255
            g = 0
            b = 0
        if color == "orange":
            r = 255
            g = 215
            b = 0
        if color == "yellow":
            r = 255
            g = 255
            b = 0
        if color == "green":
            r = 0
            g = 128
            b = 0
        if color == "blue":
            r = 0
            g = 0
            b = 255
        if color == "purple":
            r = 255
            g = 0
            b = 255
        if color == "white":
            r = 255
            g = 255
            b = 255
        if color == "clear":
            r = 0
            g = 0
            b = 0
        for x in range(int(self.board.width)+5):
            for y in range(int(self.board.height)+5):
                self.board.SetPixel(x, y, r, g, b)
        self.board = self.matrix.SwapOnVSync(self.board)

    def text_with_outline(self, word, outer_color, inner_color, font, x_pos, y_pos):
        if outer_color == "red":
            outer_color = graphics.Color(255, 0, 0)
        if outer_color == "orange":
            outer_color = graphics.Color(255, 215, 0)
        if outer_color == "yellow":
            outer_color = graphics.Color(255, 255, 0)
        if outer_color == "green":
            outer_color = graphics.Color(0, 128, 0)
        if outer_color == "blue":
            outer_color = graphics.Color(0, 0, 255)
        if outer_color == "purple":
            outer_color = graphics.Color(255, 0, 255)
        if outer_color == "white":
            outer_color = graphics.Color(255, 255, 255)
        if inner_color == "red":
            inner_color = graphics.Color(255, 0, 0)
        if inner_color == "orange":
            inner_color = graphics.Color(255, 215, 0)
        if inner_color == "yellow":
            inner_color = graphics.Color(255, 255, 0)
        if inner_color == "green":
            inner_color = graphics.Color(0, 128, 0)
        if inner_color == "blue":
            inner_color = graphics.Color(0, 0, 255)
        if inner_color == "purple":
            inner_color = graphics.Color(255, 0, 255)
        if inner_color == "white":
            inner_color = graphics.Color(255, 255, 255)
        graphics.DrawText(self.board, font, float(x_pos), float(y_pos), outer_color, word)
        graphics.DrawText(self.board, font, float(x_pos) - 1, float(y_pos), outer_color, word)
        graphics.DrawText(self.board, font, float(x_pos) + 1, float(y_pos), outer_color, word)
        graphics.DrawText(self.board, font, float(x_pos), float(y_pos) - 1, outer_color, word)
        graphics.DrawText(self.board, font, float(x_pos), float(y_pos) + 1, outer_color, word)
        graphics.DrawText(self.board, font, float(x_pos), float(y_pos), inner_color, word)

    def switch_to(self, screen_name):
        self.screens[screen_name]()

# Main function
if __name__ == "__main__":
    matrix = Matrix()
    if (not matrix.process()):
        matrix.print_help()
    c.close_connection()
