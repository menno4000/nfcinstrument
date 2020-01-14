import sys
import time
import os
from os import path
from queue import Queue

import RPi.GPIO as GPIO
from RasPi3_sequencer.util.KY040 import KY040

from RasPi3_sequencer import receiver
from RasPi3_sequencer import sequencer

GPIO.setmode(GPIO.BCM)
play_gpio = 16
reset_gpio = 20
record_gpio = 12
metro_gpio = 21
GPIO.setup(play_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(reset_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(record_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(metro_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)

ROOT_DIR = "./RasPi3_sequencer/samples/"
METRO_SAMPLES = [ROOT_DIR + "MetroBeat2.wav", ROOT_DIR + "MetroBar2.wav"]


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
    print("------------------------------------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------------------------------------")
    print("INFO - Starting Script to receive sounds from Arduino via Bluetooth and run Sequencer to make music.")

    # hardware setup for buttons and rotary knobs
    beat_knob = KY040(17, 27, 22, beat_change, beat_reset)
    bpm_knob = KY040(18, 23, 24, bpm_change, bpm_reset)
    volume_knob = KY040(5, 6, 13, volume_change, volume_reset)
    beat_knob.start()
    bpm_knob.start()
    volume_knob.start()

    # reassign root dir if given by command line argument
    if len(sys.argv) > 1:
        ROOT_DIR = sys.argv[1]

    # check if ROOT_DIR exists
    if not path.exists(ROOT_DIR):
        print("ERROR - Given root directory '%s' for samples does not exist. Exiting." % ROOT_DIR)
        sys.exit()

    # setup sound files
    sample_files = []
    for subdir, dirs, files in os.walk(ROOT_DIR):
        for directory in sorted(dirs):
            current_samples = []
            for file in os.listdir(ROOT_DIR + directory):
                if file.endswith(".wav"):
                    current_samples.append(ROOT_DIR + directory + "/" + file)
            sample_files.append(current_samples)

    # queue is used to send signals from one thread to another
    queue = Queue()

    # initialize thread for receiving signals via bluetooth
    bluetooth_input = receiver.ReceiveInput(queue)

    # initialize sequencer with threads: play & listen for input
    sequencer = sequencer.Sequencer(sample_files, METRO_SAMPLES, queue, seq_length=64, note_length=16, start_sequence=True, metro=True)

    # listen endlessly for hardware input
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
        record_button = GPIO.input(record_gpio)
        metro_button = GPIO.input(metro_gpio)
        if not play_button:
            sequencer.interpret_command("play")
            time.sleep(0.2)
        if not reset_button:
            sequencer.interpret_command("reset")
            time.sleep(0.2)
        if not record_button:
            sequencer.interpret_command("record")
            time.sleep(0.2)
        if not metro_button:
            sequencer.interpret_command("metro")
            time.sleep(0.2)
