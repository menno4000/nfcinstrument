import sys
import numpy


def kick_layout(seq_length=64, layout=1, note_length=16, note=1):
    check_for_valid_note(note)

    placement = note_length/4
    array = []
    for i in range(seq_length):
        if i%placement == 0:
            array.append(note)
        else:
            array.append(0)

    # layout 2 = kick roll
    if layout == 2:
        array[-2] = note

    return array


def snare_or_clap_layout(seq_length=64, layout=1, note_length=16, note=1):
    check_for_valid_note(note)

    placement = note_length/2
    array = []
    for i in range(seq_length):
        if (i+4)%placement == 0:
            array.append(note)
        else:
            array.append(0)
    return array


def hihat_layout(seq_length=64, layout=1, note_length=16, note=1):
    check_for_valid_note(note)

    placement = note_length/4
    array = []
    if note_length==4:
        return numpy.zeros(shape=seq_length, dtype='int8')
    elif note_length == 8:
        note_displacement = 1
    elif note_length == 16:
        note_displacement = 2
    for i in range(seq_length):
        if (i+note_displacement)%placement == 0:
            array.append(note)
        else:
            array.append(0)

    return array


def bass_layout(seq_length=64, layout=1, note_length=16, note=1, second_note=2):
    check_for_valid_note(note)
    check_for_valid_note(second_note)

    placement = note_length/4
    array = []
    if note_length == 4 or note_length == 8:
        return numpy.zeros(shape=seq_length, dtype='int8')
    for i in range(seq_length):
        if i%placement == 0:
            array.append(0)
        else:
            if layout == 1:
                array.append(note)
            elif layout == 2: # add groove
                if (i+2)%(placement*2) == 0:
                    array.append(second_note)
                else:
                    array.append(note)
    return array


def get_metronome(seq_length):
    metro_beat = [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    metro_bar = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    if seq_length == 32:
        return metro_bar, metro_beat
    elif seq_length == 64:
        return metro_bar + metro_bar, metro_beat + metro_beat


def check_for_valid_note(note):
    if note > 12 or note < 0:
        print("ERROR - Note has to be between 1 - 12")
        sys.exit()
