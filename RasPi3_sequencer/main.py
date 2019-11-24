import time
import pygame
from queue import Queue

import receiver
import sequencer

# todo's:
# two sequencer modes: running and paused
# insert sound from BT into sequence
# use led matrix to show saved notes: open thread for display


# this list contains playable sound files (please keep in order)
# 1-kick, 2-snare (or clap), 3-hihat, 4-bass,
sound_files = ['./sounds/Aubit_Kick5.wav', './sounds/Aubit_Snare3.wav', './sounds/Aubit_HatClosed5.wav', './sounds/Bass09.wav']

if __name__ == "__main__":
    print("INFO - Starting Script to receive sounds from Arduino via Bluetooth and run Sequencer to make music.")

    # queue is used to send signals from one thread to another
    queue = Queue()

    # initialize threads for receiving signals via bluetooth & starting sequencer which plays sounds
    bluetooth_input = receiver.ReceiveInput(queue)
    sequencer_loop = sequencer.Sequencer(sound_files, queue)
    while True:
        print("INFO - Script is still running...")
        time.sleep(5)
