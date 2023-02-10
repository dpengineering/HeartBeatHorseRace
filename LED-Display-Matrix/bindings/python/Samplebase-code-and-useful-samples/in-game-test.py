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

heartrate1 = 0
heartrate2 = 0
heartrate3 = 0
heartrate4 = 0
lap1 = 0
lap2 = 0
lap3 = 0
lap4 = 0
laps = 0


joyvalue = None
laps = 0

class Matrix(SampleBase):
    global laps
    def __init__(self, *args, **kwargs):
        super(Matrix, self).__init__(*args, **kwargs)

    def run(self):
        self.board = self.matrix.CreateFrameCanvas()
        self.font2 = graphics.Font()
        self.font3 = graphics.Font()

        self.font2.LoadFont("/home/pi/LED-Display-Matrix/fonts/6x13.bdf")
        self.font3.LoadFont("/home/pi/LED-Display-Matrix/fonts/7x13.bdf")
        self.font4 = graphics.Font()
        self.font4 = graphics.Font()
        self.font4.LoadFont("/home/pi/LED-Display-Matrix/fonts/retro-gaming.bdf")
        self.font5 = graphics.Font()
        self.font5.LoadFont("/home/pi/LED-Display-Matrix/fonts/ter-u24b.bdf")
        self.font6 = graphics.Font()
        self.font6.LoadFont("/home/pi/LED-Display-Matrix/fonts/ter-u24b.bdf")
        self.font7 = graphics.Font()
        self.font7.LoadFont("/home/pi/LED-Display-Matrix/fonts/retro-gaming.bdf")
        self.text_color3 = graphics.Color(255, 255, 255)
        self.text_color4 = graphics.Color(255, 0, 0)
        self.screens = {"screensaver": self.in_game()}

        self.in_game()

    def listen(self):
        global packetvalue, pack

        # original code commented out by Roshan
        # while True:
        #     pack = c.recv_packet()
        #     packetvalue = pack[1].decode()
        #     sleep(0.05)
        return

    def in_game(self):

        global packetvalue, heartrate1, heartrate2, heartrate3, heartrate4, lap1, lap2, lap3, lap4, laps

        textColor = graphics.Color(255, 0, 0)
        pos1 = self.board.width * 0.05 / 4
        pos2 = self.board.width * 1.05 / 4
        pos3 = self.board.width * 2.05 / 4
        pos4 = self.board.width * 3.05 / 4
        post1 = self.board.width * .65 / 4
        post2 = self.board.width * 1.65 / 4
        post3 = self.board.width * 2.65 / 4
        post4 = self.board.width * 3.65 / 4
        horiz1 = self.board.height * 2 / 5
        horiz2 = self.board.height * 4 / 5

        while True:
            self.board.Clear()

            len1 = self.text_with_outline("Rate:", "white", "blue", self.font3, pos1, horiz1)
            len2 = self.text_with_outline("Rate:", "white", "blue", self.font3, pos2, horiz1)
            len3 = self.text_with_outline("Rate:", "white", "blue", self.font3, pos3, horiz1)
            len4 = self.text_with_outline("Rate:", "white", "blue", self.font3, pos4, horiz1)

            len9 = self.text_with_outline(str(heartrate1), "white", "blue", self.font3, post1, horiz1)
            len10 = self.text_with_outline(str(heartrate2), "white", "blue", self.font3, post2, horiz1)
            len11 = self.text_with_outline(str(heartrate3), "white", "blue", self.font3, post3, horiz1)
            len12 = self.text_with_outline(str(heartrate4), "white", "blue", self.font3, post4, horiz1)

            len5 = self.text_with_outline("Laps:", "white", "blue", self.font3, pos1, horiz2)
            len6 = self.text_with_outline("Laps:", "white", "blue", self.font3, pos2, horiz2)
            len7 = self.text_with_outline("Laps:", "white", "blue", self.font3, pos3, horiz2)
            len8 = self.text_with_outline("Laps:", "white", "blue", self.font3, pos4, horiz2)

            len13 = self.text_with_outline(str(lap1) + "/3", "white", "blue", self.font3, post1, horiz2)
            len14 = self.text_with_outline(str(lap2) + "/3", "white", "blue", self.font3, post2, horiz2)
            len15 = self.text_with_outline(str(lap3) + "/3", "white", "blue", self.font3, post3, horiz2)
            len16 = self.text_with_outline(str(lap4) + "/3", "white", "blue", self.font3, post4, horiz2)

            time.sleep(0.1)
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



# Main function
if __name__ == "__main__":
    matrix = Matrix()
    if (not matrix.process()):
        matrix.print_help()
