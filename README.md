# HeartBeatHorseRace
Four oDrives, four LEDs Displays, two Raspberry PIs, four bluetooth heartrate sensors, four horses, and a dream;

**Current State:** You should be worrying about two files: **main.py** and **Matrix.py**. On start up, one of the raspberry PIs, which displays the kivy screen, controls the oDrives, and connects to the bluetooth heartrate sensors, runs **main.py**, while the other raspberry PI, which controls the LED Displays, runs **Matrix.py.** Packets of information are sent back and forth between RPIs through a DPEA-P2P connection. Learn more information about P2P [here](https://github.com/dpengineering/dpea-p2p).

**Useful information:**
* Hold the heart rate sensors properly! This is probably the most important information, and will be the most important factor on whether the program will crash or not. If the program crashes, turn the power off and on again.
* As of right now (February 2022), only POLAR adapters/heartrate sensors work for horses 1 - 3. Horse 4 can move fine, but we don't have a functioning POLAR sensor for it yet.
* For some reason, the sensors will stop working if you take out the POLAR adapters and put them back in. You need to wait a long time before they start working again. We're not sure as to why this happens.
* **main.py** and files that control the horses/heartrate sensors can be found in the folder **HorseRaceGame**. Moreover, **Matrix.py** and files that control the LED Displays can be found folders in **LED-Display-Matrix --> bindings --> python --> samples**. Learn more information about the LED-Displays [here](https://github.com/dpengineering/LED-Display).
------------------------
Written by `@foongi` and `@landonhellmandpea`.

For any questions with the project feel free to reach out. 

Ethan Foong:  
ivethan5@gmail.com

Landon Hellman:  
landonhellman0@gmail.com

Note: When you contact us please let us know who you are and that this is for the HeartBeatHorseRace so we don't accidently ignore you.
