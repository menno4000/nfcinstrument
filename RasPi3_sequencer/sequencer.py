import sys
import threading
import time
import numpy
import pygame
import enum
from threading import Thread

#import displayer
import util


# methods for sequencer:
# start/stop
# reset sequence
# give start presets: constant kick, kick pattern etc.

class Channels(enum.Enum):
    Kick = 0
    Snare = 1
    HiHat = 2
    Bass = 3
    MetroBar = 4
    MetroBeat = 5


def get_channels_and_sounds(list_of_sounds):
    pygame.mixer.init(frequency=44100, size=-16, channels=8, buffer=2 ** 12)

    print("SEQ_INFO - Setting up '%s' channels and loading wav-files into sound objects." % amount_of_sounds)
    sounds = []
    amount_of_sounds = 13
    for i in range(len(list_of_sounds)):
        sound_channel_list = [0] * amount_of_sounds
        for j in range(amount_of_sounds):
            sound_channel_list[j] = pygame.mixer.Sound(list_of_sounds[i][j])
        sounds.append(sound_channel_list)
    channels = [pygame.mixer.Channel(i)] * len(sounds)

    sounds[0].set_volume(1.0)
    sounds[1].set_volume(0.5)
    sounds[2].set_volume(0.2)

    return channels, sounds


def get_sequencer(sequence_length, amount_of_sounds, init=[]):
    sequencer = numpy.zeros(shape=(amount_of_sounds, sequence_length), dtype='int8')

    print("SEQ_INFO - Loading example Sequencer Layout")
    sequencer[0] = util.kick_layout(1, sequence_length)
    sequencer[1] = util.snare_or_clap_layout(1, sequence_length)
    sequencer[2] = util.hihat_layout(1, sequence_length)
    #sequencer[3] = util.bass_layout(1, sequence_length)

    show_sequencer_layout(sequencer)
    displayer.print_sequencer(sequencer, sequence_length)
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

    def __init__(self, list_of_sounds, queue, seq_length=32, bars=2, start_sequence=True, metro=False):
        self.play = start_sequence

        # sequencer
        self.bars = bars
        self.sequence_length = seq_length  # 2 bars, 16th notes, 4 are one beat
        self.channels, self.sounds = get_channels_and_sounds(list_of_sounds)
        self.seq = get_sequencer(self.sequence_length, len(self.channels))

        self.beat = 0
        self.beat_to_program = -1
        self.current_channel = 0 # start on kick channel
        self.max_channels = len(self.channels)

        # timing
        self.delay_factor = 0.8
        self.bpm = 120.0
        self.ibb = (60.0 / self.bpm) / 8.0  # interval between beats
        self.metro = metro

        # times the intervals between notes
        self.timerThread = threading.Event()

        print("SEQ_INFO - Start listening thread to receive data.")
        self.listening_thread = Thread(target=self.listen_for_bt_input, args=(queue,))
        self.listening_thread.start()

        #displayer.give_info(self.bars, self.sequence_length, len(self.channels), self.seq)

        print("SEQ_INFO - Start playing loaded values.")
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def interpret_command(self, command):
        if command == "play" or command == "pause":
            self.play = not self.play
            displayer.print_text(command, self.seq)
        elif command == "reset":
            #self.seq = get_sequencer(self.sequence_length, len(self.channels))
            self.seq[self.current_channel] = numpy.zeros(shape=self.sequence_length, dtype='int8')
            self.beat = 0
            displayer.print_text(command, self.seq)
        elif command == "show":
            displayer.give_info(self.bars, self.sequence_length, len(self.channels), self.seq)
        elif command == "metro":
            self.toggle_metronome()
        elif not self.play:
            try:
                beat = int(command)
                if 1 <= beat <= 32:
                    self.beat_to_program = beat-1
                    displayer.print_text("note %s" % beat, self.seq)
            except ValueError:
                print('Could not find interpretation for your command. Received command: %s' % command)
        else:
            print('Could not find interpretation for your command. Received command: %s' % command)

    def listen_for_hardware_input(self):
        command = ""
        # bpm change through scroll
        # beat change through scroll
        # button for play/pause
        if 1:
            command = "play"
        # button for reset
        if 2:
            command = "reset"
        # button for metro on/off
        if 3:
            command = "metro"
        self.interpret_command("play")

    def toggle_metronome(self):
        self.metro = not self.metro
        if self.metro:
            metro_bar, metro_beat = util.metronome(self.sequence_length)
            self.seq[4] = metro_bar
            self.seq[5] = metro_beat
        if not self.metro:
            self.seq[4] = numpy.zeros(shape=1, dtype='int8')
            self.seq[5] = numpy.zeros(shape=1, dtype='int8')

    def listen_for_bt_input(self, queue):
        while (True):
            data = queue.get()
            channel = self.current_channel
            # check for channel switching: #+ or #-
            if data[0] == "#":
                if data[1] == "+":
                    if channel == self.max_channels:
                        self.current_channel = 0
                    else:
                        self.current_channel += 1
                    print("SEQ_INFO - Raised current channel.")
                elif data[1] == "-":
                    if channel == 0:
                        self.current_channel = self.max_channels
                    else:
                        self.current_channel -= 1
                    print("SEQ_INFO - Decreased current channel.")
                else:
                    print("ERROR - Identifier is not valid for channel switching. Received data: %s." % data)
                displayer.print_text("switched channel to: %s" % Channels(self.current_channel).name)

            # identifier '%' defines setting a new sound into the sequencer
            elif data[0] == "%":
                note = int(data[1:])
                if 0 < note <= 13: # accepting notes for a full octave + one more --> 13 notes, 1-13
                    if not self.play and self.beat_to_program > 0:
                        print("SEQ_INFO - Found new sound - Channel: %s:%s, Beat: %s" % (channel, Channels(channel), self.beat_to_program))
                        self.seq[channel][self.beat_to_program] = note
                    else:
                        print("SEQ_INFO - Found new sound - Channel: %s:%s, Beat: %s" % (channel, Channels(channel), self.beat))
                        self.seq[channel][self.beat] = note
                else:
                    print("ERROR - Note could not be evaluated. Received data: %s." % data)
            else:
                print("SEQ_INFO - Could not evaluate bluetooth command. Received data: %s." % data)
            displayer.print_sequencer(self.seq, self.sequence_length)

    # method which runs the sequencer and plays sounds accordingly
    def run(self):
        while not self.timerThread.wait(self.ibb):
            if self.play:
                then = time.time()
                # if value in channel > 0, play sound
                if self.seq[0][self.beat] != 0:
                    self.channels[0].play(self.sounds[self.seq[0][self.beat]])
                if self.seq[1][self.beat] != 0:
                    self.channels[1].play(self.sounds[self.seq[0][self.beat]])
                if self.seq[2][self.beat] != 0:
                    self.channels[2].play(self.sounds[self.seq[0][self.beat]])
                if self.seq[3][self.beat] != 0:
                    self.channels[3].play(self.sounds[self.seq[0][self.beat]])
                #if self.seq[4][self.beat] != 0:
                #    self.channels[4].play(self.sounds[4])
                #if self.seq[5][self.beat] != 0:
                #    self.channels[5].play(self.sounds[5])

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
