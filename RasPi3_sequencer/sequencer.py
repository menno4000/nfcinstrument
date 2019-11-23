import threading
import time
import numpy
import pygame


def get_channels_and_sounds(list_of_sounds):
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=2 ** 12)

    amount_of_sounds = len(list_of_sounds)
    print(f"INFO - Setting up {amount_of_sounds} channels and loading wav-files into sound objects.")
    channels = [0] * 16
    sounds = [0] * 16
    for i in range(amount_of_sounds):
        channels[i] = pygame.mixer.Channel(i)
        sounds[i] = pygame.mixer.Sound(list_of_sounds[i])

    sounds[0].set_volume(1.0)
    sounds[1].set_volume(0.5)

    return channels, sounds


def get_sequencer(sequence_length):
    sequencer = numpy.zeros(shape=(4, sequence_length), dtype='int8')

    print("INFO - Loading example Sequencer Layout")
    # 1 1 1 1 | 1 1 1 1 | 1 1 1 1 | 1 1 1 1 | - kick drum,  sequencer[0]
    # 0 1 0 1 | 0 1 0 1 | 0 1 0 1 | 0 1 0 1 | - clap,       sequencer[1]
    for i in range(sequence_length):
        if (i % 4) == 0:
            sequencer[0][i] = 1
        if (i+4)%8 == 0:
            sequencer[1][i] = 1

    sequencer[2] = [0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0,   0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0,   0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0,   0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0]
    # sequencer[3] = [0,1,1,1, 0,1,1,1, 0,1,1,1, 0,1,1,1,   0,1,1,1, 0,1,1,1, 0,1,1,1, 0,1,1,1,   0,1,1,1, 0,1,1,1, 0,1,1,1, 0,1,1,1,   0,1,1,1, 0,1,1,1, 0,1,1,1, 0,1,1,1]
    #sequencer[3] = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, ]

    show_sequencer_layout(sequencer)
    return sequencer


def show_sequencer_layout(sequencer):
    print("INFO - Sequencer Layout")
    print("------------------------------------------------------------------------------------------------")

    print("Bar -\t\t 1_______2_______3_______4_______5_______6_______7_______8_______")
    print(f"KICK -\t\t{sequencer[0][32:]} ...")
    print(f"SNARE -\t\t{sequencer[1][32:]} ...")
    print(f"HIHAT -\t\t{sequencer[2][32:]} ...")
    print(f"BASS -\t\t{sequencer[3][32:]} ...")
    print("Beat - \t\t 1 2 3 4 5 6 7 8 9 10  12  14  16  18  20  22  24  26  28  30  32")
    print("Beat - \t\t                     11  13  15  17  19  21  23  25  27  29  31")
    print("------------------------------------------------------------------------------------------------")


class Sequencer(object):

    def __init__(self, list_of_sounds):
        self.delay_factor = 0.8
        self.bpm = 145
        self.ibb = 60 / self.bpm / 4  # interval between beats
        self.sequence_length = 64  # 4 bars, 16th notes, 4 are one beat

        self.channels, self.sounds = get_channels_and_sounds(list_of_sounds)
        self.seq = get_sequencer(self.sequence_length)

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        print("INFO - Start playing loaded values.")
        thread.start()

    def run(self):
        while (True):
            for beat in range(self.sequence_length):
                then = time.time()
                # if value in channel = 1, play sound
                if self.seq[0][beat] != 0:
                    self.channels[0].play(self.sounds[0])
                if self.seq[1][beat] != 0:
                    self.channels[1].play(self.sounds[1])
                if self.seq[2][beat] != 0:
                    self.channels[2].play(self.sounds[2])
                if self.seq[3][beat] != 0:
                    self.channels[3].play(self.sounds[3])
                now = time.time()
                sleepy = float(self.ibb - (now - then))
                if sleepy > 0.0:
                    time.sleep(sleepy)
