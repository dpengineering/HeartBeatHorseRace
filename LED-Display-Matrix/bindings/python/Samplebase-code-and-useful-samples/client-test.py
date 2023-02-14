import enum
from p2p.dpea_p2p import Client
import time
from time import sleep
from samplebase import SampleBase
from rgbmatrix import graphics
from pidev.Joystick import Joystick
import os
import board
import busio
import adafruit_vl6180x

class PacketType(enum.Enum):
    COMMAND0 = 0
    COMMAND1 = 1
    COMMAND2 = 2
    COMMAND3 = 3

#         |Server IP     |Port |Packet enum
c = Client("172.17.21.3", 5001, PacketType)
c.connect()

heartrate1 = 0
heartrate2 = 0
heartrate3 = 0
heartrate4 = 0

print("poggers")

class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel")

    def run(self):
        global heartrate1, heartrate2, heartrate3, heartrate4
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("/home/pi/LED-Display-Matrix/fonts/7x13.bdf")
        textColor = graphics.Color(255, 0, 0)
        pos1 = offscreen_canvas.width * 0.35 / 4
        pos2 = offscreen_canvas.width * 1.35 / 4
        pos3 = offscreen_canvas.width * 2.35 / 4
        pos4 = offscreen_canvas.width * 3.35 / 4
        p = offscreen_canvas.height * 1 / 2

        while True:
            pack = c.recv_packet()
            x = str(pack[0])
            print(pack[0])
            print(pack[1])
            if x == "PacketType.COMMAND0":
                heartrate1 = pack[1].decode()
            elif x == "PacketType.COMMAND1":
                heartrate2 = pack[1].decode()
            elif x == "PacketType.COMMAND2":
                heartrate3 = pack[1].decode()
            elif x == "PacketType.COMMAND3":
                heartrate4 = pack[1].decode()
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos1, p, textColor, str(heartrate1))
            len1 = graphics.DrawText(offscreen_canvas, font, pos2, p, textColor, str(heartrate2))
            len2 = graphics.DrawText(offscreen_canvas, font, pos3, p, textColor, str(heartrate3))
            len3 = graphics.DrawText(offscreen_canvas, font, pos4, p, textColor, str(heartrate4))
            time.sleep(0.1)

            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)



# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()


c.close_connection()