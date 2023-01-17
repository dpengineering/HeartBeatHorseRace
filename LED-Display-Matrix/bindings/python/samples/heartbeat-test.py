from samplebase import SampleBase
from rgbmatrix import graphics
from binascii import hexlify
import pygatt
import time

adapter0 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM0')
adapter1 = pygatt.BGAPIBackend(serial_port='/dev/ttyACM1')

heartrate0 = 0
heartrate1 = 0
timeInSeconds = 0

def handle_data_for_player(player_num):
    def handle_data(handle, value):
        """
        handle -- integer, characteristic read handle the data was received on
        value -- bytearray, the data returned in the notification
        """
        #print("Received data: %s" % hexlify(value))
        if player_num == 0:
            heartrate0 = int(hexlify(value)[2:4])
        elif player_num == 1:
            heartrate1 = int(hexlify(value)[2:4])


    return handle_data

class Timer(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Timer, self).__init__(*args, **kwargs)

    def timeInSeconds_increase(self):
        global timeInSeconds
        timeInSeconds += 1
        time.sleep(1)
        return timeInSeconds

    def run(self):
        global heartrate1, heartrate0
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../../fonts/7x13.bdf")
        textColor = graphics.Color(255, 0, 0)
        pos1 = self.matrix.width * 0 / 4
        pos2 = self.matrix.width * 1 / 4
        pos3 = self.matrix.width * 2 / 4
        pos4 = self.matrix.width * 3 / 4
        try:
            adapter0.start()
            adapter1.start()

            chest_polar = adapter0.connect("C6:4B:DF:A5:36:0B")
            hand_polar = adapter1.connect("A0:9E:1A:49:A8:51")

            chest_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(0))

            hand_polar.subscribe("00002a37-0000-1000-8000-00805f9b34fb", callback=handle_data_for_player(1))

            while True:
                offscreen_canvas.Clear()
                len1 = graphics.DrawText(offscreen_canvas, font, pos1, 10, textColor, str(heartrate0))
                len2 = graphics.DrawText(offscreen_canvas, font, pos2, 10, textColor, str(heartrate1))
                len3 = graphics.DrawText(offscreen_canvas, font, pos3, 10, textColor, str(timeInSeconds))
                len4 = graphics.DrawText(offscreen_canvas, font, pos4, 10, textColor, str(timeInSeconds))

                self.timeInSeconds_increase()
                offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

        finally:
            adapter0.stop()
            adapter1.stop()

# Main function
if __name__ == "__main__":
    run_text = Timer()
    if (not run_text.process()):
        print('didnt run')
        run_text.print_help()
