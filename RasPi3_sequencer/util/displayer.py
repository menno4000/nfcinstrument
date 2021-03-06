import time

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

# create matrix device
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=16, block_orientation=-90, rotate=0)
deviceText = max7219(serial, cascaded=4, block_orientation=-90, rotate=0)
virtual = viewport(device, width=device.width, height=device.height)


def print_sequencer(sequencer, seq_length=32, note_length=16):
    max = 64
    if seq_length > max:
        print("ERROR - Can't show sequence lengths longer then '%s'." % max)
    elif seq_length <= 32:
        with canvas(device) as draw:
            text(draw, (0, 0), "Bar's:", fill="white", font=proportional(LCD_FONT))
            if note_length == 4:
                text(draw, (32, 0), "1 3 5 7", fill="white", font=proportional(TINY_FONT))
            elif note_length == 8:
                text(draw, (32, 0), "1 2 3 4", fill="white", font=proportional(TINY_FONT))
            elif note_length == 16:
                text(draw, (32, 0), "1   2   ", fill="white", font=proportional(TINY_FONT))
            else:
                return

            # display sequencer values
            for y in range(len(sequencer) - 2):
                for x in range(len(sequencer[y])):
                    if sequencer[y][x] != 0:
                        point = x+64, y
                        draw.point(point, fill="white")
    elif seq_length <= 64:
        with canvas(device) as draw:
            if note_length == 4:
                text(draw, (0, 0), "1 3 5 7", fill="white", font=proportional(TINY_FONT))
                text(draw, (64, 0), "9 111315", fill="white", font=proportional(TINY_FONT))
            elif note_length == 8:
                text(draw, (0, 0), "1 2 3 4", fill="white", font=proportional(TINY_FONT))
                text(draw, (64, 0), "5 6 7 8", fill="white", font=proportional(TINY_FONT))
            elif note_length == 16:
                text(draw, (0, 0), "1   2   ", fill="white", font=proportional(TINY_FONT))
                text(draw, (64, 0), "3   4   ", fill="white", font=proportional(TINY_FONT))
            else:
                return

            # display sequencer values
            for y in range(len(sequencer) - 2):
                for x in range(len(sequencer[y])):
                    if sequencer[y][x] != 0:
                        if x > 31:
                            point = x+64, y
                        else:
                            point = x+32, y
                        draw.point(point, fill="white")


def print_text(message, seq, note_length, wait=1.0):
    with canvas(virtual) as draw:
        text(draw, (0, 0), message, fill="white", font=proportional(LCD_FONT))
    time.sleep(wait)
    print_sequencer(seq, seq_length=len(seq[0]), note_length=note_length)


def give_info(sequencer):
    with canvas(virtual) as draw:
        text(draw, (0, 0), "Sequ", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (32, 0), "encer", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (64, 0), "leng", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (96, 0), "ths:", fill="white", font=proportional(SINCLAIR_FONT))
    time.sleep(3)

    with canvas(virtual) as draw:
        text(draw, (0, 0), str(sequencer.bars), fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (32, 0), "bars,", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (64, 0), str(sequencer.note_length), fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (96, 0), "notes", fill="white", font=proportional(SINCLAIR_FONT))
    time.sleep(3)

    with canvas(virtual) as draw:
        text(draw, (0, 0), "Chann", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (32, 0), "els:", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (64, 0), str(sequencer.max_channels) + ",", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (96, 0), "order:", fill="white", font=proportional(SINCLAIR_FONT))
    time.sleep(3)

    with canvas(virtual) as draw:
        text(draw, (0, 0), "Kick", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (32, 0), "Snare", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (64, 0), "HiHat", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (96, 0), "Bass", fill="white", font=proportional(SINCLAIR_FONT))
    time.sleep(3)

    with canvas(virtual) as draw:
        text(draw, (0, 0), "Let's", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (32, 0), "go!", fill="white", font=proportional(SINCLAIR_FONT))
    time.sleep(3)

    print_sequencer(sequencer.seq, seq_length=sequencer.sequence_length, note_length=sequencer.note_length)


def log_sequencer_layout(sequencer):
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


def log_sequencer_infos(sequencer):
    print("------------------------------------------------------------------------------------------------")
    print("Sequencer infos:")
    print()
    print("Amount of channels: %s" % len(sequencer.channels))
    print("Max Channels: %s" % sequencer.max_channels)
    print("Amount of sounds: %s = %s * %s" % (len(sequencer.sounds)*len(sequencer.sounds[0]), len(sequencer.sounds), len(sequencer.sounds[0])))
    print()
    print("Sequence length: %s" % sequencer.sequence_length)
    print("Note length: %s" % sequencer.note_length)
    print("Amount of bars: %s" % sequencer.bars)
    print("Sequencer running? %s" % sequencer.play)
    print("Metronome on? %s" % sequencer.metro)
    print("bpm: %s" % sequencer.bpm)
    print("ibs: %s" % sequencer.ibs)
    print()
    print("current Sequencer status:")
    print(sequencer.seq)
    print("------------------------------------------------------------------------------------------------")