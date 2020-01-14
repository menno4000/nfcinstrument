import threading
import time
import numpy
import enum
from threading import Thread

from .util import displayer
from .util import layouter
from .util import seq_setup

MAX_NOTE = 12


class Channels(enum.Enum):
    Kick = 0
    Snare = 1
    HiHat = 2
    Bass = 3


class Sequencer(object):

    def __init__(self, list_of_samples, metro_samples, queue, seq_length=32, note_length=16, start_sequence=True, metro=False):
        self.play = start_sequence
        self.metro = metro

        # sequencer
        self.note_length = note_length
        self.sequence_length = seq_length
        self.bars = seq_length/note_length

        self.channels, self.sounds, self.metro_sounds = seq_setup.get_channels_and_sounds(list_of_samples, metro_samples, MAX_NOTE)
        self.seq = seq_setup.get_sequencer(seq_length=self.sequence_length, amount_of_sounds=len(self.channels), note_length=self.note_length)

        self.cursor = 0
        self.beat_to_program = -1
        self.current_channel = 0
        self.max_channels = len(self.channels) - 2
        self.volume = 0.75
        self.record = True

        # timing
        self.bpm = 120.0
        self.ibs = (60.0 / self.bpm) / (note_length/4) # time between each note (interval between sounds: ibs)

        # times the intervals between notes
        self.timerThread = threading.Event()

        print("SEQ_INFO - Start listening threads to receive bluetooth & hardware data.")
        self.bt_thread = Thread(target=self.listen_for_bt_input, args=(queue,))
        self.bt_thread.start()

        #displayer.give_info(self)
        displayer.log_sequencer_infos(self)

        print("SEQ_INFO - Start playing loaded values.")
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()

    def interpret_command(self, command):
        if command == "play":
            self.cursor = 0
            self.play = not self.play
            if self.play:
                displayer.print_text("play", self.seq, self.note_length)
            else:
                displayer.print_text("pause", self.seq, self.note_length)
        elif command == "reset":
            self.seq[self.current_channel] = numpy.zeros(shape=self.sequence_length, dtype='int8')
            self.cursor = 0
            displayer.print_text("reset channel      %s" % Channels(self.current_channel).name, self.seq, self.note_length)
        elif command == "record":
            self.record = not self.record
            if self.record:
                print("SEQ_INFO - Changing to record mode.")
                displayer.print_text("recor d", self.seq, self.note_length)
            else:
                print("SEQ_INFO - Changing to preview mode.")
                displayer.print_text("previ ew", self.seq, self.note_length)
        elif command == "metro":
            self.toggle_metronome()
        elif 'beat' in command:
            self.change_beat(command)
        elif 'bpm' in command:
            command = command.split('_')[1]
            if command == 'up':
                self.bpm += 2
            elif command == "down":
                self.bpm -= 2
            elif command == "reset":
                self.bpm = 120
            self.ibs = (60.0 / self.bpm) / (self.note_length/4)
            displayer.print_text("bpm:   %s" % self.bpm, self.seq, self.note_length, wait=0.3)
        elif command == "volume_up":
            self.change_volume('+')
        elif command == "volume_down":
            self.change_volume('-')
        elif command == "volume_reset":
            self.change_volume('/')
        elif command == "show":
            displayer.give_info(self.seq)
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

    def change_beat(self, command):
        command = command.split('_')[1]
        info_text = ""
        if command == 'reset':
            self.cursor = 0
            self.beat_to_program = 0
            info_text = "beat  reset"
        else:
            if self.play:
                info_text = "pause for.  featu.re"
            elif command == "up":
                if self.beat_to_program == self.sequence_length-1:
                    self.beat_to_program = 0
                else:
                    self.beat_to_program += 1
                    info_text = "beat:  %s" % str(self.beat_to_program + 1)
            elif command == "down":
                if self.beat_to_program == 0:
                    self.beat_to_program = self.sequence_length-1
                else:
                    self.beat_to_program -= 1
                info_text = "beat:  %s" % str(self.beat_to_program + 1)
        if not info_text == "":
            displayer.print_text(info_text, self.seq, self.note_length, wait=0.3)

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
        displayer.print_text("vol    set.to%s" % new_volume, self.seq, self.note_length, wait=0.3)

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
                try:
                    note = int(data[1:])
                except: # neccessary because sometimes we get spliced bluetooth messages
                    print("SEQ_ERROR - Could not evaluate data '%s'." % data)
                    continue
                if self.record:
                    if 0 < note <= MAX_NOTE: # accepting notes for a full octave + one more --> 12 notes, 1-12
                        if not self.play and self.beat_to_program > 0:
                            print("SEQ_INFO - Record new sound - Channel: %s-%s, Beat: %s" % (channel, Channels(self.current_channel).name, self.beat_to_program))
                            self.seq[channel][self.beat_to_program] = note
                        else:
                            print("SEQ_INFO - Record new sound - Channel: %s-%s, Beat: %s" % (channel, Channels(self.current_channel).name, self.cursor))
                            self.seq[channel][self.cursor] = note
                    else:
                        print("ERROR - Note could not be evaluated. Received data: %s." % data)
                else:
                    print("SEQ_INFO - Playing sound - Channel: %s-%s" % (channel, Channels(self.current_channel).name))
                    current_sound_channel = self.sounds[channel]
                    self.channels[channel].play(current_sound_channel[note])

            else:
                print("SEQ_INFO - Could not evaluate bluetooth command. Received data: %s." % data)
            displayer.print_sequencer(self.seq, seq_length=self.sequence_length, note_length=self.note_length)

    # method which runs the sequencer and plays sounds accordingly
    def run(self):
        while not self.timerThread.wait(self.ibs):
            if self.play:
                # play metronome
                if self.metro:
                    max_chan = self.max_channels
                    if self.seq[max_chan][self.cursor] != 0:
                        self.channels[max_chan].play(self.metro_sounds[0])
                    elif self.seq[max_chan + 1][self.cursor] != 0:
                        self.channels[max_chan + 1].play(self.metro_sounds[1])

                # loop through channels, if value in channel > 0, play sound
                for i in range(self.max_channels):
                    if self.seq[i][self.cursor] != 0:
                        current_sound_channel = self.sounds[i]
                        note_to_play = self.seq[i][self.cursor] - 1
                        self.channels[i].play(current_sound_channel[note_to_play])

                # reset beat & loop
                if self.cursor >= self.sequence_length-1:
                    self.cursor = 0
                else:
                    self.cursor += 1
