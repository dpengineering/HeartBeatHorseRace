# LED Display
Below is an Adafruit guide on how to get started<br />
https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi?view=all<br /><br />
These are the commands to clone and setup the repository for creating Python programs to run on the LED matrix<br />
```
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/rgb-matrix.sh >rgb-matrix.sh
sudo bash rgb-matrix.sh
```
Make sure when running the script to select **Adafruit RGB Matrix HAT + RTC** and **Convenience**<br /><br />
Then build for Python3 in the **LED-Display/bindings/python/** directory using the commands below<br />
```
sudo apt update && sudo apt install python3-dev python3-pillow -y
sudo make build-python PYTHON=$(command -v python3)
sudo make install-python PYTHON=$(command -v python3)
```
Below is an example with flags on how to run your Python program<br />
```
sudo python3 main.py --led-cols=128 --led-rows=32 -b 50 --led-slowdown-gpio=3 -m adafruit-hat
```
