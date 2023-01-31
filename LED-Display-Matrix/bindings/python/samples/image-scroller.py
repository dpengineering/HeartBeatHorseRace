#!/usr/bin/env python
import time
from samplebase import SampleBase
from PIL import Image
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

font4 = graphics.Font()
font4.LoadFont("/home/pi/LED-Display-Matrix/fonts/6x10.bdf")


image = Image.open("/home/pi/LED-Display-Matrix/img/Heart_Button.png")
text_color4 = graphics.Color(255, 255, 255)


class ImageScroller(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ImageScroller, self).__init__(*args, **kwargs)
        self.parser.add_argument("-i", "--image", help="The image to display", default="/home/pi/LED-Display-Matrix/img/Heart_Button.png")

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

    def run(self):

        options = RGBMatrixOptions()
        options.cols = 64
        options.rows = 32
        options.chain_length = 4
        options.parallel = 1
        options.gpio_slowdown = 3
        options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'



        if not 'image' in self.__dict__:
            self.image = Image.open("/home/pi/LED-Display-Matrix/img/Heart_Button.png").convert('RGB')
            self.image2 = Image.open("/home/pi/LED-Display-Matrix/img/Heart_Button.png").convert('RGB')
        self.image.resize((int(self.matrix.width * 0.5), int(self.matrix.height * 0.5)), Image.ANTIALIAS)
        self.image.thumbnail((int(self.matrix.width * 0.5), int(self.matrix.height * 0.5)), Image.ANTIALIAS)

        self.image2.resize((int(self.matrix.width * 0.6), int(self.matrix.height * 0.6)), Image.ANTIALIAS)
        self.image2.thumbnail((int(self.matrix.width * 0.6), int(self.matrix.height * 0.6)), Image.ANTIALIAS)

        self.board = self.matrix.CreateFrameCanvas()
        text1 = "Taking"
        text2 = ["Heartrate", "Heartrate.", "Heartrate.."]
        i = 0
        p = 0
        # let's scroll
        while True:
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



            graphics.DrawText(self.board, font4, 0, 23, text_color4, text1)
            graphics.DrawText(self.board, font4, 0, 31, text_color4, text2[i])

            graphics.DrawText(self.board, font4, self.board.width * 1/4, 23, text_color4, text1)
            graphics.DrawText(self.board, font4, self.board.width * 1/4, 31, text_color4, text2[i])

            graphics.DrawText(self.board, font4, self.board.width * 2/4, 23, text_color4, text1)
            graphics.DrawText(self.board, font4, self.board.width * 2/4, 31, text_color4, text2[i])

            graphics.DrawText(self.board, font4, self.board.width * 3/4, 23, text_color4, text1)
            graphics.DrawText(self.board, font4, self.board.width * 3/4, 31, text_color4, text2[i])

            p = p + 1
            i = i + 1
            if i == 3:
                i = 0
            self.board = self.matrix.SwapOnVSync(self.board)

            time.sleep(0.5)
            self.board.Clear()


# Main function
# e.g. call with
#  sudo ./image-scroller.py --chain=4
# if you have a chain of four
if __name__ == "__main__":
    image_scroller = ImageScroller()
    if (not image_scroller.process()):
        image_scroller.print_help()
