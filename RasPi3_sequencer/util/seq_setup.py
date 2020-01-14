import pygame
import numpy

from . import displayer
from . import layouter

DEFAULT_VOLUME = 0.5


def get_channels_and_sounds(list_of_samples, metro_sounds, max_note):
    sounds = []
    amount_of_channels = len(list_of_samples) + 2
    amount_of_sounds = max_note

    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=8, buffer=2 ** 12)
    pygame.mixer.set_num_channels(amount_of_channels)
    channels = [0] * amount_of_channels

    print("SEQ_INFO - Setting up '%s' channels and loading wav-files into sound objects." % amount_of_channels)

    for i in range(len(list_of_samples)):
        sound_channel_list = [0] * amount_of_sounds
        for j in range(amount_of_sounds):
            sound_channel_list[j] = pygame.mixer.Sound(list_of_samples[i][j])
            sound_channel_list[j].set_volume(DEFAULT_VOLUME)
        sounds.append(sound_channel_list)
        channels[i] = pygame.mixer.Channel(i)

    # add metronome: 2 more channels, 2 sounds
    channels[amount_of_channels - 1] = pygame.mixer.Channel(amount_of_channels - 1)
    channels[amount_of_channels - 2] = pygame.mixer.Channel(amount_of_channels - 2)

    metro_beat_sound = pygame.mixer.Sound(metro_sounds[0])
    metro_bar_sound = pygame.mixer.Sound(metro_sounds[1])

    return channels, sounds, [metro_beat_sound, metro_bar_sound]


def get_sequencer(seq_length=64, amount_of_sounds=4, note_length=16):
    sequencer = numpy.zeros(shape=(amount_of_sounds, seq_length), dtype='int8')

    #print("SEQ_INFO - Loading example Sequencer Layout")
    #sequencer[0] = layouter.kick_layout(seq_length=seq_length, layout=2, note_length=note_length, note=2)
    #sequencer[1] = layouter.snare_or_clap_layout(seq_length=seq_length, layout=1, note_length=note_length, note=2)
    #sequencer[2] = layouter.hihat_layout(seq_length=seq_length, layout=1, note_length=note_length, note=8)
    #sequencer[3] = layouter.bass_layout(seq_length=seq_length, layout=2, note_length=note_length, note=2, second_note=3)

    # set metronome layout
    sequencer[amount_of_sounds - 1], sequencer[amount_of_sounds - 2] = layouter.get_metronome(seq_length)

    if seq_length == 32:
        displayer.log_sequencer_layout(sequencer)
    displayer.print_sequencer(sequencer, seq_length=seq_length, note_length=note_length)
    return sequencer
