import threading
import time
import numpy
import pygame
from threading import Thread

import displayer


# methods for sequencer:
# start/stop
# reset sequence
# give start presets: constant kick, kick pattern etc.

def get_channels_and_sounds(list_of_sounds):
    pygame.mixer.init(frequency=44100, size=-16, channels=8, buffer=2 ** 12)

    amount_of_sounds = len(list_of_sounds)
    print("SEQ_INFO - Setting up '%s' channels and loading wav-files into sound objects." % amount_of_sounds)
    channels = [0] * 16
    sounds = [0] * 16
    for i in range(amount_of_sounds):
        channels[i] = pygame.mixer.Channel(i)
        sounds[i] = pygame.mixer.Sound(list_of_sounds[i])

    sounds[0].set_volume(1.0)
    sounds[1].set_volume(0.5)
    sounds[2].set_volume(0.5)

    return channels, sounds


def kick_layout(layout):
    if layout == 1: # "four to the floor"
        return [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    if layout == 2: # "four to the floor with kick roll"
        return [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0]
    if layout == 3: # experimental
        return [1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0]


def snare_or_clap_layout(layout):
    if layout == 1: # classcial on every second beat
        return [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    if layout == 2: # experimental
        return [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0]


def hihat_layout(layout):
    if layout == 1: # classical: offbeat
        return [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
    if layout == 2: # all
        return [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


def get_sequencer(sequence_length, amount_of_sounds):
    sequencer = numpy.zeros(shape=(amount_of_sounds, sequence_length), dtype='int8')

    print("SEQ_INFO - Loading example Sequencer Layout")
    sequencer[0] = kick_layout(1)
    sequencer[1] = snare_or_clap_layout(1)
    #sequencer[2] = hihat_layout(2)

    show_sequencer_layout(sequencer)
    displayer.print_sequencer(sequencer)
    return sequencer


def show_sequencer_layout(sequencer):
    print("SEQ_INFO - Sequencer Layout")
    print("------------------------------------------------------------------------------------------------")

    print("Bar -\t\t 1_______2_______3_______4_______5_______6_______7_______8_______")
    print("KICK -\t\t%s ..." % sequencer[0])
    print("SNARE -\t\t%s ..." % sequencer[1])
    print("HIHAT -\t\t%s ..." % sequencer[2])
    print("BASS -\t\t%s ..." % sequencer[3])
    print("Beat - \t\t 1 2 3 4 5 6 7 8 9 10  12  14  16  18  20  22  24  26  28  30  32")
    print("Beat - \t\t                     11  13  15  17  19  21  23  25  27  29  31")
    print("------------------------------------------------------------------------------------------------")


class Sequencer(object):

    def __init__(self, list_of_sounds, queue):
        self.beat = 0
        self.delay_factor = 0.8
        self.bpm = 120.0
        self.ibb = (60.0 / 120.0) / 4.0  # interval between beats
        self.sequence_length = 32  # 4 bars, 8th notes, 8 are one beat

        self.channels, self.sounds = get_channels_and_sounds(list_of_sounds)
        self.seq = get_sequencer(self.sequence_length, len(self.channels))

        thread = threading.Thread(target=self.run)
        thread.daemon = True
        print("SEQ_INFO - Start listening thread to receive data")
        listening_thread = Thread(target=self.check_for_new_tones, args=(queue, ))
        listening_thread.start()

        print("SEQ_INFO - Start playing loaded values.")
        thread.start()

    def check_for_new_tones(self, queue):
        while (True):
            channel = int(queue.get())
            if channel > -1:
                print("SEQ_INFO - Found new sound - Channel: %s, Beat: %s" % (channel, self.beat))
                self.seq[channel][self.beat] = 1
                displayer.print_sequencer(self.seq)

    def run(self):
        while (True):
            then = time.time()
            # if value in channel = 1, play sound
            if self.seq[0][self.beat] != 0:
                self.channels[0].play(self.sounds[0])
            if self.seq[1][self.beat] != 0:
                self.channels[1].play(self.sounds[1])
            if self.seq[2][self.beat] != 0:
                self.channels[2].play(self.sounds[2])
            if self.seq[3][self.beat] != 0:
                self.channels[3].play(self.sounds[3])

            # 0 < beat < 31
            if self.beat >= 31:
                self.beat = 0
            else:
                self.beat += 1
            #print(self.beat)

            now = time.time()
            sleepy = float(self.ibb - (now - then))
            if sleepy > 0.0:
                time.sleep(sleepy)
