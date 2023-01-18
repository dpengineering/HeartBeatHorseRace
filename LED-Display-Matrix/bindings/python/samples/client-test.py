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
    NULL = 0
    COMMAND1 = 1
    COMMAND2 = 2

#         |Server IP     |Port |Packet enum
c = Client("172.17.21.3", 5001, PacketType)
c.connect()

print("poggers")

class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel")

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../../../fonts/7x13.bdf")
        textColor = graphics.Color(255, 0, 0)
        pos = offscreen_canvas.width * 1.35 / 4
        p = offscreen_canvas.height * 1 / 2

        while True:
            pack = c.recv_packet()
            heartrate = pack[1].decode()
            len = graphics.DrawText(offscreen_canvas, font, pos, p, textColor, heartrate)
            time.sleep(2)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)


# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()


c.close_connection()