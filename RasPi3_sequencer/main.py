import sys
import os
from queue import Queue

import receiver
import sequencer

# todo's:
# two sequencer modes: running and paused
# give option to enable sequencer with default values
# insert sound from BT into sequence -> make good data format
# create samples, create samples for whole octave
# switch between sequence beats


# this list contains playable sound files (please keep in order)
# 1-kick, 2-snare (or clap), 3-hihat, 4-bass,
sound_files = ['./sounds/Aubit_Kick5.wav', './sounds/Aubit_Snare3.wav', './sounds/Aubit_HatClosed5.wav', './sounds/Bass09.wav', './sounds/MetroBar2.wav', './sounds/MetroBeat2.wav']

if __name__ == "__main__":
    print("INFO - Starting Script to receive sounds from Arduino via Bluetooth and run Sequencer to make music.")

    # queue is used to send signals from one thread to another
    queue = Queue()

    # initialize threads for receiving signals via bluetooth & starting sequencer which plays sounds
    #bluetooth_input = receiver.ReceiveInput(queue)

    # setup sound files
    rootdir = "./samples/"
    sample_files = []
    for subdir, dirs, files in os.walk(rootdir):
        for directory in sorted(dirs):
            current_samples = []
            for file in os.listdir(rootdir + directory):
                if file.endswith(".wav"):
                    current_samples.append(rootdir + directory + "/" + file)
            sample_files.append(current_samples)

    # examples:
    # sequencer_loop = sequencer.Sequencer(sound_files, queue, seq_length=32, bars=2, start_sequence=True)
    sequencer_loop = sequencer.Sequencer(sample_files, queue, seq_length=64, bars=4, start_sequence=True)
    while True:
        print("INFO - Script is still running...")

        print("INFO - You can type some keywords to control the sequencer via cmd.")
        print("'play/pause' - starts/pauses sequencer, 'reset' - to delete sequenced beats")
        print("'show' - displays current configuration, 'metro' - toggles metronome on/off")
        print("In paused mode you can type any number of the sequence and program the sequencer for that point of time.")
        command = input()
        sequencer_loop.interpret_cmd(command)
