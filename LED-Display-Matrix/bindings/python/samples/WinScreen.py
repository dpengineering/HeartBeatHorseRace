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


class PacketType(enum.Enum):
    COMMAND0 = 0
    COMMAND1 = 1
    COMMAND2 = 2
    COMMAND3 = 3

#          |Server IP           |Port |Packet enum
c = Client("172.17.21.3", 5001, PacketType)

joyvalue = None
laps = 0

class Matrix(SampleBase):
    global laps
    def __init__(self, *args, **kwargs):
        super(Matrix, self).__init__(*args, **kwargs)

    def run(self):
        self.board = self.matrix.CreateFrameCanvas()

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
        self.screens = {"screensaver": self.idle_screen()}

        self.idle_screen()

    def listen(self):
        global packetvalue, pack

        # original code commented out by Roshan
        while True:
            pack = c.recv_packet()
            packetvalue = pack[1].decode()
            sleep(0.05)
    def idle_screen(self):

        global packetvalue, heartrate1, heartrate2, heartrate3, heartrate4, lap1, lap2, lap3, lap4, laps

        packetvalue = None
        pos = self.board.width
        length = graphics.DrawText(self.board, self.font5, pos, 23, self.text_color4, "HEARTBEAT HORSE RACE")

        y_offset = [20, 21, 22, 23, 24, 25, 26, 27, 28, 27, 26, 25, 24, 23, 22, 21]
        y1 = 0
        y2 = 4
        y3 = 8
        y4 = 12

        self.board = self.matrix.CreateFrameCanvas()



        while True:

            # big tippy maze text
            self.board.Clear()
            self.text_with_outline("Win!", "white", "blue", self.font5, 10, y_offset[y1])
            self.text_with_outline("Lose", "white", "red", self.font6, self.board.width/4+8, y_offset[y2])
            self.text_with_outline("Lose", "white", "red", self.font6, self.board.width*2/4+8, y_offset[y3])
            self.text_with_outline("Lose", "white", "red", self.font6, self.board.width*3/4+8, y_offset[y4])


            y1 = y1 + 1
            y2 = y2 + 1
            y3 = y3 + 1
            y4 = y4 + 1
            if y1 == 16:
                y1 = 0
            elif y2 == 16:
                y2 = 0
            elif y3 == 16:
                y3 = 0
            elif y4 == 16:
                y4 = 0

            sleep(0.06)
            if (pos + length < 0):
                pos = self.board.width

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
