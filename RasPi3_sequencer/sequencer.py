import threading
import time
import numpy
import pygame
import enum
from threading import Thread

from .util import displayer
from .util import layouter

DEFAULT_VOLUME = 0.5


class Channels(enum.Enum):
    Kick = 0
    Snare = 1
    HiHat = 2
    Bass = 3
    #MetroBar = 4
    #MetroBeat = 5


def get_channels_and_sounds(list_of_sounds):
    sounds = []
    amount_of_channels = len(list_of_sounds)
    amount_of_sounds = 12

    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=8, buffer=2 ** 12)
    pygame.mixer.set_num_channels(amount_of_channels)
    channels = [0] * amount_of_channels

    print("SEQ_INFO - Setting up '%s' channels and loading wav-files into sound objects." % amount_of_channels)

    for i in range(amount_of_channels):
        sound_channel_list = [0] * amount_of_sounds
        for j in range(amount_of_sounds):
            sound_channel_list[j] = pygame.mixer.Sound(list_of_sounds[i][j])
            sound_channel_list[j].set_volume(DEFAULT_VOLUME)
        sounds.append(sound_channel_list)
        channels[i] = pygame.mixer.Channel(i)

    return channels, sounds


def get_sequencer(seq_length=64, amount_of_sounds=4, note_length=16):
    sequencer = numpy.zeros(shape=(amount_of_sounds, seq_length), dtype='int8')

    print("SEQ_INFO - Loading example Sequencer Layout")
    sequencer[0] = layouter.kick_layout(seq_length=seq_length, layout=2, note_length=note_length, note=2)
    sequencer[1] = layouter.snare_or_clap_layout(seq_length=seq_length, layout=1, note_length=note_length, note=2)
    sequencer[2] = layouter.hihat_layout(seq_length=seq_length, layout=1, note_length=note_length, note=8)
    sequencer[3] = layouter.bass_layout(seq_length=seq_length, layout=2, note_length=note_length, note=2, second_note=3)

    if seq_length == 32:
        displayer.show_sequencer_layout(sequencer)
    displayer.print_sequencer(sequencer, seq_length=seq_length, note_length=note_length)
    return sequencer


class Sequencer(object):

    def __init__(self, list_of_sounds, queue, seq_length=32, note_length=16, start_sequence=True, metro=False):
        self.play = start_sequence

        # sequencer
        self.note_length = note_length
        self.sequence_length = seq_length
        self.bars = seq_length/note_length
        self.channels, self.sounds = get_channels_and_sounds(list_of_sounds)
        self.seq = get_sequencer(seq_length=self.sequence_length, amount_of_sounds=len(self.channels), note_length=self.note_length)

        self.beat = 0
        self.beat_to_program = -1
        self.current_channel = 0 # start on kick channel
        self.max_channels = len(self.channels)
        self.volume = 0.75

        # timing
        self.bpm = 120.0
        # time between each note (interval between beats: ibb)
        self.ibb = (60.0 / self.bpm) / (note_length/4)
        self.metro = metro

        # times the intervals between notes
        self.timerThread = threading.Event()

        print("SEQ_INFO - Start listening threads to receive bluetooth & hardware data.")
        self.bt_thread = Thread(target=self.listen_for_bt_input, args=(queue,))
        self.bt_thread.start()

        #displayer.give_info(self)

        print("SEQ_INFO - Start playing loaded values.")
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def interpret_command(self, command):
        if command == "play":
            self.beat = 0
            self.play = not self.play
            if self.play:
                displayer.print_text("play", self.seq, self.note_length)
            else:
                displayer.print_text("pause", self.seq, self.note_length)
        elif command == "reset":
            self.seq[self.current_channel] = numpy.zeros(shape=self.sequence_length, dtype='int8')
            self.beat = 0
            displayer.print_text("reset channel      %s" % Channels(self.current_channel).name, self.seq, self.note_length)
        elif command == "show":
            displayer.give_info(self)
        elif command == "metro":
            self.toggle_metronome()
        elif 'beat' in command:
            command = command.split('_')[1]
            if command == 'reset':
                self.beat = 0
                self.beat_to_program = 0
                displayer.print_text("beat  reset", self.seq, self.note_length)
            elif command == "up":
                if self.play:
                    displayer.print_text("pause for.  featu.re", self.seq, self.note_length)
                else:
                    if self.beat_to_program == self.sequence_length-1:
                        self.beat_to_program = 0
                    else:
                        self.beat_to_program += 1
                    displayer.print_text("beat:  %s" % str(self.beat_to_program + 1), self.seq, self.note_length)
            elif command == "down":
                if self.play:
                    displayer.print_text("pause for.  featu.re", self.seq, self.note_length)
                else:
                    if self.beat_to_program == 0:
                        self.beat_to_program = self.sequence_length-1
                    else:
                        self.beat_to_program -= 1
                    displayer.print_text("beat:  %s" % str(self.beat_to_program + 1), self.seq, self.note_length)
        elif 'bpm' in command:
            command = command.split('_')[1]
            if command == 'up':
                self.bpm += 2
            elif command == "down":
                self.bpm -= 2
            elif command == "reset":
                self.bpm = 120
            self.ibb = (60.0 / self.bpm) / (self.note_length/4)
            displayer.print_text("bpm:   %s" % self.bpm, self.seq, self.note_length)
        elif command == "volume_up":
            self.change_volume('+')
        elif command == "volume_down":
            self.change_volume('-')
        elif command == "volume_reset":
            self.change_volume('/')
        else:
            print('Could not find interpretation for your command. Received command: %s' % command)

    def toggle_metronome(self):
        self.metro = not self.metro
        if self.metro:
            metro_bar, metro_beat = layouter.get_metronome(self.sequence_length)
            self.seq[4] = metro_bar
            self.seq[5] = metro_beat
        if not self.metro:
            self.seq[4] = numpy.zeros(shape=1, dtype='int8')
            self.seq[5] = numpy.zeros(shape=1, dtype='int8')

    def change_volume(self, identifier):
        sound_channel = self.sounds[self.current_channel]
        new_volume = sound_channel[0].get_volume()
        if identifier == '+':
            new_volume += 0.05
        elif identifier == '-':
            new_volume -= 0.05
        elif identifier == '/':
            new_volume = 0.75
        else:
            print("ERROR - Could not find a valid identifier to change volume. Identifier: %s" % identifier)
            return
        for sound in sound_channel:
            sound.set_volume(new_volume)
        displayer.print_text("vol    set.to%s" % new_volume, self.seq, self.note_length)

    def listen_for_bt_input(self, queue):
        while (True):
            data = queue.get()
            channel = self.current_channel
            # check for channel switching: #+ or #-
            if data[0] == "#":
                if data[1] == "+":
                    if channel == self.max_channels-1:
                        self.current_channel = 0
                    else:
                        self.current_channel += 1
                    print("SEQ_INFO - Raised current channel.")
                elif data[1] == "-":
                    if channel == 0:
                        self.current_channel = self.max_channels-1
                    else:
                        self.current_channel -= 1
                    print("SEQ_INFO - Decreased current channel.")
                else:
                    print("ERROR - Identifier is not valid for channel switching. Received data: %s." % data)
                displayer.print_text("Chann el     %s" % Channels(self.current_channel).name, self.seq, self.note_length)

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
            displayer.print_sequencer(self.seq, seq_length=self.sequence_length, note_length=self.note_length)

    # method which runs the sequencer and plays sounds accordingly
    def run(self):
        while not self.timerThread.wait(self.ibb):
            if self.play:
                # if value in channel > 0, play sound
                for i in range(self.max_channels):
                    if self.seq[i][self.beat] != 0:
                        current_sound_channel = self.sounds[i]
                        note_to_play = self.seq[i][self.beat] - 1
                        self.channels[i].play(current_sound_channel[note_to_play])

                # reset beat & loop
                if self.beat >= self.sequence_length-1:
                    self.beat = 0
                else:
                    self.beat += 1
