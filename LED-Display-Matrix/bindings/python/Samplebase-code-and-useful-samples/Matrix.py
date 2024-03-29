# This is the main file you will be using to control the LED Display on the Heartbeat Horse Race. If you read on dpea p2p,
# you can learn more about how to send signals back and forth from the matrix.py raspberry pi and the main.py raspberry pi.
# These two files run simultaneously. For us, we developed both files on separate computers at the same time, connecting main.py
# to matrix.py as we tested code.

# There are a several helper files we are leaving in to educate you on how to use the LED board system to display images,
# and text. Namely, image-scroller will help you learn to run images, and WinScreen or in-game-test will help you display
# text. If you'd like to make your own images pixel by pixel, the tippy maze repo may help you learn that.

# Samplebase is a very important file that Matrix.py is a child file of. We don't understand that file too well, but
# what is important in that file is that it helps you set the settings for the LED matrix you are using. So if you end
# changing the size of the LED matrix (using a different product or something), go to samplebase and scroll to the area
# where you tell the file the size of the LED matrix you are using.


# Other than that, there's not too much I can help you learn about/do, just read through this file and see what you can
# gain. Then, move on and try to improve the project! Thanks for working on it!

import time
import sys
from time import sleep
from samplebase import SampleBase
from rgbmatrix import graphics
import os
import board
import busio
import adafruit_vl6180x
import enum
sys.path.append("/home/pi/")
from p2p.dpea_p2p import Client
from threading import Thread
from datetime import datetime
from PIL import Image
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C(), pwm_frequency=400.0) # this will change the pwm_frequency to 250Hz
kit.motor1.throttle = 0

from adafruit_motorkit import MotorKit

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

# Here is where we define the martix.py file as the client side of the server
#          |Server IP           |Port |Packet enum
c = Client("172.17.21.3", 5001, PacketType)

# Connecting to the server
c.connect()

joyvalue = None

# Samplebase
class Matrix(SampleBase):
    global laps
    def __init__(self, *args, **kwargs):
        super(Matrix, self).__init__(*args, **kwargs)
        Thread(target=self.listen, daemon=True).start()

    # Run is called by the function at the bottom of this file, it loads all the fonts, creats the matrix (LED screen)
    # and does basically all the setup  for the screens
    def run(self):
        self.board = self.matrix.CreateFrameCanvas()
        self.font2 = graphics.Font()

        # loads some fonts
        self.font2.LoadFont("/home/pi/LED-Display-Matrix/fonts/7x13.bdf")
        self.font4 = graphics.Font()
        self.font4.LoadFont("/home/pi/LED-Display-Matrix/fonts/retro-gaming.bdf")
        self.font5 = graphics.Font()
        self.font5.LoadFont("/home/pi/LED-Display-Matrix/fonts/ter-u24b.bdf")
        self.font6 = graphics.Font()
        self.font6.LoadFont("/home/pi/LED-Display-Matrix/fonts/6x10.bdf")
        self.font7 = graphics.Font()
        self.font7.LoadFont("/home/pi/LED-Display-Matrix/fonts/retro-gaming.bdf")
        self.text_color3 = graphics.Color(255, 255, 255)
        self.text_color4 = graphics.Color(255, 0, 0)

        self.idle_screen()

    # Listen is the interface for the server between the two raspberry pis. This is called on the matrix's creation
    # it runs on a separate thread from all the other code, allowing the file to listen for data and display things at
    # the same time.
    def listen(self):
        global packetvalue, pack

        # original code commented out by Roshan
        while True:
            pack = c.recv_packet()
            packetvalue = pack[1].decode()
            sleep(0.05)

    # First screen for when the project is started and idle.
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
            self.text_with_outline("HEART", "white", "blue", self.font5, 2, y_offset[y1])
            self.text_with_outline("BEAT", "white", "blue", self.font5, self.board.width/4+8, y_offset[y2])
            self.text_with_outline("HORSE", "white", "blue", self.font5, self.board.width*2/4+2, y_offset[y3])
            self.text_with_outline("RACE", "white", "blue", self.font5, self.board.width*3/4+8, y_offset[y4])

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

            # This is how the matrix detects that the main.py raspberry pi is ready for it to switch screens.
            if str(packetvalue) == 'baseline':
                self.board.Clear()
                break

            if str(packetvalue) == 'quitting':
                self.board.Clear()
                quit()

        self.baseline()

    # Screen for taking the baseline heartrate of players.
    def baseline(self):

        if not 'image' in self.__dict__:
            self.image = Image.open("/home/pi/LED-Display-Matrix/img/Heart_Button.png").convert('RGB')
            self.image2 = Image.open("/home/pi/LED-Display-Matrix/img/Heart_Button.png").convert('RGB')
            print("yee")
        self.image.resize((int(self.matrix.width * 0.5), int(self.matrix.height * 0.5)), Image.ANTIALIAS)
        self.image.thumbnail((int(self.matrix.width * 0.5), int(self.matrix.height * 0.5)), Image.ANTIALIAS)

        self.image2.resize((int(self.matrix.width * 0.6), int(self.matrix.height * 0.6)), Image.ANTIALIAS)
        self.image2.thumbnail((int(self.matrix.width * 0.6), int(self.matrix.height * 0.6)), Image.ANTIALIAS)

        text1 = "Taking"
        text2 = ["Heartrate", "Heartrate.", "Heartrate.."]
        i = 0
        p = 0
        while True:
            if p % 101 == 0:
                if p % 2 == 0:
                    self.board.SetImage(self.image, 34, 2)
                    self.board.SetImage(self.image, 34 + 64, 2)
                    self.board.SetImage(self.image, 34 + 128, 2)
                    self.board.SetImage(self.image, 34 + 192, 2)
                else:
                    self.board.SetImage(self.image2, 30, 2)
                    self.board.SetImage(self.image2, 30 + 64, 2)
                    self.board.SetImage(self.image2, 30 + 128, 2)
                    self.board.SetImage(self.image2, 30 + 192, 2)



                graphics.DrawText(self.board, self.font6, 0, 23, self.text_color3, text1)
                graphics.DrawText(self.board, self.font6, 0, 31, self.text_color3, text2[i])

                graphics.DrawText(self.board, self.font6, self.board.width * 1/4, 23, self.text_color3, text1)
                graphics.DrawText(self.board, self.font6, self.board.width * 1/4, 31, self.text_color3, text2[i])

                graphics.DrawText(self.board, self.font6, self.board.width * 2/4, 23, self.text_color3, text1)
                graphics.DrawText(self.board, self.font6, self.board.width * 2/4, 31, self.text_color3, text2[i])

                graphics.DrawText(self.board, self.font6, self.board.width * 3/4, 23, self.text_color3, text1)
                graphics.DrawText(self.board, self.font6, self.board.width * 3/4, 31, self.text_color3, text2[i])
                self.board = self.matrix.SwapOnVSync(self.board)

                self.board.Clear()
                i = i + 1
                if i == 3:
                    i = 0

            time.sleep(0.005)
            p = p + 1


            print(packetvalue)
            if str(packetvalue) == 'start':
                self.board.Clear()
                break

            if str(packetvalue) == 'error':
                self.board.Clear()
                self.idle_screen()

        self.countdown_screen()

    # The 3, 2, 1, Go! screen.
    def countdown_screen(self):
        print("yeezy")

        self.text_with_outline("3", "white", "blue", self.font5, 26, 23)
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(1)
        self.board.Clear()
        self.text_with_outline("2", "white", "blue", self.font5, self.board.width / 4 + 26, 23)
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(1)
        self.board.Clear()
        self.text_with_outline("1", "white", "blue", self.font5, self.board.width * 2/4 + 26, 23)
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(1)
        self.board.Clear()
        self.text_with_outline("Go!", "white", "blue", self.font5, self.board.width * 3 / 4 + 16, 23)
        self.board = self.matrix.SwapOnVSync(self.board)
        sleep(1)
        self.in_game()

    # This screen displays a player's heartrate and laps completed during the game.
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
            # We can use packetvalue within the loop here to get all the lap/heartrate data.
            packetType = str(pack[0])

            # Our lap + heartrate data comes in the form: "(Heartrate #)-(lap #)" - ex: 25-2 for 25 bpm, 2 laps completed
            # this if statement helps us decode that data.
            if "-" in packetvalue:
                 x = packetvalue.split("-")
                 packetvalue = x[0]
                 laps = x[1]


            if packetType == "PacketType.COMMAND0":
                heartrate1 = packetvalue
                lap1 = laps
            elif packetType == "PacketType.COMMAND1":
                heartrate2 = packetvalue
                lap2 = laps
            elif packetType == "PacketType.COMMAND2":
                heartrate3 = packetvalue
                lap3 = laps
            elif packetType == "PacketType.COMMAND3":
                heartrate4 = packetvalue
                lap4 = laps
            self.board.Clear()

            len1 = self.text_with_outline("Rate:", "white", "blue", self.font2, pos1, horiz1)
            len2 = self.text_with_outline("Rate:", "white", "blue", self.font2, pos2, horiz1)
            len3 = self.text_with_outline("Rate:", "white", "blue", self.font2, pos3, horiz1)
            len4 = self.text_with_outline("Rate:", "white", "blue", self.font2, pos4, horiz1)

            len9 = self.text_with_outline(str(heartrate1), "white", "blue", self.font2, post1, horiz1)
            len10 = self.text_with_outline(str(heartrate2), "white", "blue", self.font2, post2, horiz1)
            len11 = self.text_with_outline(str(heartrate3), "white", "blue", self.font2, post3, horiz1)
            len12 = self.text_with_outline(str(heartrate4), "white", "blue", self.font2, post4, horiz1)

            len5 = self.text_with_outline("Laps:", "white", "blue", self.font2, pos1, horiz2)
            len6 = self.text_with_outline("Laps:", "white", "blue", self.font2, pos2, horiz2)
            len7 = self.text_with_outline("Laps:", "white", "blue", self.font2, pos3, horiz2)
            len8 = self.text_with_outline("Laps:", "white", "blue", self.font2, pos4, horiz2)

            len13 = self.text_with_outline(str(lap1) + "/3", "white", "blue", self.font2, post1, horiz2)
            len14 = self.text_with_outline(str(lap2) + "/3", "white", "blue", self.font2, post2, horiz2)
            len15 = self.text_with_outline(str(lap3) + "/3", "white", "blue", self.font2, post3, horiz2)
            len16 = self.text_with_outline(str(lap4) + "/3", "white", "blue", self.font2, post4, horiz2)

            self.board = self.matrix.SwapOnVSync(self.board)
            print(packetvalue)
            if str(packetvalue) == 'WIN':
                if packetType == "PacketType.COMMAND0":
                    self.win_screen(1)
                elif packetType == "PacketType.COMMAND1":
                    self.win_screen(2)
                elif packetType == "PacketType.COMMAND2":
                    self.win_screen(3)
                elif packetType == "PacketType.COMMAND3":
                    self.win_screen(4)


    # Screen after one player wins
    def win_screen(self, number):
        self.board.Clear()

        y_offset = [20, 21, 22, 23, 24, 25, 26, 27, 28, 27, 26, 25, 24, 23, 22, 21]
        y1 = 0
        y2 = 4
        y3 = 8
        y4 = 12

        while True:

            # big tippy maze text
            self.board.Clear()
            if number == 1:
                self.text_with_outline("Win!", "white", "blue", self.font5, 10, y_offset[y1])
                self.text_with_outline("Lose", "white", "red", self.font5, self.board.width / 4 + 8, y_offset[y2])
                self.text_with_outline("Lose", "white", "red", self.font5, self.board.width * 2 / 4 + 8, y_offset[y3])
                self.text_with_outline("Lose", "white", "red", self.font5, self.board.width * 3 / 4 + 8, y_offset[y4])
            elif number == 2:
                self.text_with_outline("Win!", "white", "blue", self.font5, self.board.width / 4 + 10, y_offset[y1])
                self.text_with_outline("Lose", "white", "red", self.font5, 10, y_offset[y2])
                self.text_with_outline("Lose", "white", "red", self.font5, self.board.width * 2 / 4 + 8, y_offset[y3])
                self.text_with_outline("Lose", "white", "red", self.font5, self.board.width * 3 / 4 + 8, y_offset[y4])
            elif number == 3:
                self.text_with_outline("Win!", "white", "blue", self.font5, self.board.width * 2/4 + 10, y_offset[y1])
                self.text_with_outline("Lose", "white", "red", self.font5, self.board.width / 4 + 8, y_offset[y2])
                self.text_with_outline("Lose", "white", "red", self.font5, 10, y_offset[y3])
                self.text_with_outline("Lose", "white", "red", self.font5, self.board.width * 3 / 4 + 8, y_offset[y4])
            elif number == 4:
                self.text_with_outline("Win!", "white", "blue", self.font5, self.board.width * 3/4 + 10, y_offset[y1])
                self.text_with_outline("Lose", "white", "red", self.font5, self.board.width / 4 + 8, y_offset[y2])
                self.text_with_outline("Lose", "white", "red", self.font5, self.board.width * 2 / 4 + 8, y_offset[y3])
                self.text_with_outline("Lose", "white", "red", self.font5, 10, y_offset[y4])


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

            self.board = self.matrix.SwapOnVSync(self.board)
            print(packetvalue)
            if str(packetvalue) == "done":
                self.idle_screen()

    # Helper function I'm unsure we even use anymore - helps display the packetvalue text when run.
    def run_text(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../../../fonts/7x13.bdf")
        textColor = graphics.Color(255, 0, 0)
        pos = offscreen_canvas.width * 1.35 / 4
        p = offscreen_canvas.height * 1 / 2

        while True:
            pack = c.recv_packet()
            heartrate = pack[1].decode()
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, p, textColor, heartrate)
            time.sleep(2)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

    # Quits out of the server
    def quitting(self):
        if c.recv_packet() == (PacketType.COMMAND0, b'quit'):
            c.close_connection()
            quit()

    # Helper function to add a colored border around a text font
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


# Main function - basically just runs Matrix.py run function.
if __name__ == "__main__":
    matrix = Matrix()

    if (not matrix.process()):
        matrix.print_help()
