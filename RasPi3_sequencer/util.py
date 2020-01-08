def kick_layout(layout, seq_length):
    four_to_the_floor = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    ftff_kick_roll = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0]
    experimental = [1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0]

    if seq_length == 32:
        if layout == 1:
            return four_to_the_floor
        if layout == 2:
            return ftff_kick_roll
        if layout == 3:
            return experimental
    elif seq_length == 64:
        if layout == 1:
            return four_to_the_floor + four_to_the_floor
        if layout == 2:
            return ftff_kick_roll + ftff_kick_roll
        if layout == 3:
            return experimental + experimental


def snare_or_clap_layout(layout, seq_length):
    classcial = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    experimental = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0]
    if seq_length == 32:
        if layout == 1:
            return classcial
        if layout == 2:
            return experimental
    elif seq_length == 64:
        if layout == 1:
            return classcial + classcial
        if layout == 2:
            return experimental + experimental


def hihat_layout(layout, seq_length):
    offbeat = [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]
    all = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    if seq_length == 32:
        if layout == 1:
            return offbeat
        if layout == 2:
            return all
    elif seq_length == 64:
        if layout == 1:
            return offbeat + offbeat
        if layout == 2:
            return all + all


def bass_layout(layout, seq_length):
    triple_b = [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1]
    if seq_length == 32:
        if layout == 1:
            return triple_b
    elif seq_length == 64:
        if layout == 1:
            return triple_b + triple_b


def metronome(seq_length):
    metro_beat =    [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
    metro_bar =     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    if seq_length == 32:
        return metro_bar, metro_beat
    elif seq_length == 64:
        return metro_bar + metro_bar, metro_beat + metro_beat