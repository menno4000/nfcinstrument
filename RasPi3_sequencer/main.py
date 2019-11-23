import time
import pygame

#import receiver
import sequencer

# todo's:
# log outputs
# two classes, one main file
# two sequencer modes: running and paused
# use led matrix to show saved notes

# this list contains playable sound files (please keep in order)
# 1-kick, 2-snare (or clap), 3-hihat, 4-bass,
sound_files = ['./sounds/Aubit_Kick5.wav', './sounds/Aubit_Snare3.wav', './sounds/Aubit_HatClosed5.wav', './sounds/Bass09.wav']

if __name__ == "__main__":
    print("INFO - Starting Script to receive sounds from Arduino via Bluetooth and run Sequencer to make music.")
    #bluetooth_input = receiver.ReceiveInput()
    sequencer_loop = sequencer.Sequencer(sound_files)
    while True:
        print("INFO - Script is still running...")
        time.sleep(5)
