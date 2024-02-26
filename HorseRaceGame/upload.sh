#!/usr/bin/env bash

# Uploads and executes Matrix.py on the Raspberry Pi in charge of the display

# Delete existing instance of Heart Beat Horse Race project on the Raspberry Pi, if it exists
if [[ `ssh pi@heartbeat-horse-race-matrix.local test -d /home/pi/Documents/full_code/HorseRaceGame/ && echo exists` ]] ; then
  ssh pi@heartbeat-horse-race-matrix.local -f 'rm -rf /home/pi/Documents/full_code/HorseRaceGame/';
fi

# Copy HorseRaceGame/ and dpea_p2p/ directories to Raspberry Pi
scp -pr /home/pi/Documents/full_code/HorseRaceGame/ pi@heartbeat-horse-race-matrix.local:/home/pi/Documents/full_code/


# Execute Matrix.py
echo "Executing Matrix.py on Raspberry Pi"
ssh pi@heartbeat-horse-race-matrix.local 'python3 /home/pi/Documents/full_code/LED-Display-Matrix/bindings/python/Samplebase-code-and-useful-samples/Matrix.py'
echo "Matrix.py executed on Raspberry Pi"
