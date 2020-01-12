import sys
import time
import os
from queue import Queue

import RPi.GPIO as GPIO
from RasPi3_sequencer.util.KY040 import KY040

from RasPi3_sequencer import receiver
from RasPi3_sequencer import sequencer

GPIO.setmode(GPIO.BCM)
play_gpio = 16
reset_gpio = 20
GPIO.setup(play_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(reset_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# metro sounds: MetroBeat2.wav, MetroBar2.wav


def beat_change(direction):
    if direction == 1:
        sequencer.interpret_command("beat_up")
    else:
        sequencer.interpret_command("beat_down")


def beat_reset(direction):
    sequencer.interpret_command("beat_reset")


def bpm_change(direction):
    if direction == 1:
        sequencer.interpret_command("bpm_up")
    else:
        sequencer.interpret_command("bpm_down")


def bpm_reset(direction):
    sequencer.interpret_command("bpm_reset")


def volume_change(direction):
    if direction == 1:
        sequencer.interpret_command("volume_up")
    else:
        sequencer.interpret_command("volume_down")


def volume_reset(direction):
    sequencer.interpret_command("volume_reset")


if __name__ == "__main__":
    print("INFO - Starting Script to receive sounds from Arduino via Bluetooth and run Sequencer to make music.")

    # queue is used to send signals from one thread to another
    queue = Queue()

    # initialize threads for receiving signals via bluetooth & starting sequencer which plays sounds
    bluetooth_input = receiver.ReceiveInput(queue)

    # hardware setup for buttons and rotary knobs
    beat_knob = KY040(17, 27, 22, beat_change, beat_reset)
    bpm_knob = KY040(18, 23, 24, bpm_change, bpm_reset)
    volume_knob = KY040(5, 6, 13, volume_change, volume_reset)
    beat_knob.start()
    bpm_knob.start()
    volume_knob.start()

    # setup sound files
    rootdir = "./RasPi3_sequencer/samples/"
    sample_files = []
    for subdir, dirs, files in os.walk(rootdir):
        for directory in sorted(dirs):
            current_samples = []
            for file in os.listdir(rootdir + directory):
                if file.endswith(".wav"):
                    current_samples.append(rootdir + directory + "/" + file)
            sample_files.append(current_samples)

    # examples:
    #sequencer = sequencer.Sequencer(sample_files, queue, seq_length=32, note_length=16, start_sequence=True)
    sequencer = sequencer.Sequencer(sample_files, queue, seq_length=64, note_length=16, start_sequence=True)
    while True:
        # control bluetooth input with commandline
        #print("INFO - You can type some keywords to control the sequencer via cmd.")
        #print("'play' - starts/pauses sequencer, 'reset' - to delete saved sequence for current channel")
        #print("'show' - displays current configuration, 'metro' - toggles metronome on/off")
        #print("'beat_reset', 'beat_up' & 'beat_down'")
        #print("'bpm_reset', 'bpm_up', 'bpm_down'")
        #print("'volume_reset', 'volume_up', 'volume_down'")
        #command = input()
        #if '#' in command or '%' in command:
        #    queue.put(str(command, 'utf-8'))
        #else:
        #    sequencer_loop.interpret_command(command)

        play_button = GPIO.input(play_gpio)
        reset_button = GPIO.input(reset_gpio)
        if not play_button:
            sequencer.interpret_command("play")
        if not reset_button:
            sequencer.interpret_command("reset")
        # button for metro on/off
        # button to switch between preview & record mode
