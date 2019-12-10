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


def print_sequencer(sequencer, seq_length):
    max = 64
    if seq_length > max:
        print("ERROR - Can't show sequence lengths longer then '%s'." % max)
        return
    if seq_length <= 32:
        with canvas(device) as draw:
            text(draw, (0, 0), "Beat's", fill="white", font=proportional(LCD_FONT))
            text(draw, (32, 0), "1 3 5 7", fill="white", font=proportional(TINY_FONT))
            for y in range(len(sequencer)):
                for x in range(len(sequencer[y])):
                    if sequencer[y][x] == 1:
                        point = x+64, y
                        draw.point(point, fill="white")
    else:
        with canvas(device) as draw:
            text(draw, (0, 0), "1 3 5 7", fill="white", font=proportional(TINY_FONT))
            text(draw, (64, 0), "9 111315", fill="white", font=proportional(TINY_FONT))
            for y in range(len(sequencer)):
                for x in range(len(sequencer[y])):
                    if sequencer[y][x] == 1:
                        #print("x: %s, y: %s" % (x, y))
                        if x > 31:
                            point = x+64, y
                        else:
                            point = x+32, y
                        draw.point(point, fill="white")


def print_text(message, seq):
    with canvas(virtual) as draw:
        text(draw, (0, 0), message, fill="white", font=proportional(LCD_FONT))
    time.sleep(1)
    print_sequencer(seq, len(seq[0]))


def give_info(bars, sequence_length, amount_of_channels, seq):
    with canvas(virtual) as draw:
        text(draw, (0, 0), "Sequ", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (32, 0), "encer", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (64, 0), "leng", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (96, 0), "ths:", fill="white", font=proportional(SINCLAIR_FONT))
    time.sleep(3)

    with canvas(virtual) as draw:
        text(draw, (0, 0), str(bars), fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (32, 0), "bars,", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (64, 0), str(sequence_length), fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (96, 0), "notes", fill="white", font=proportional(SINCLAIR_FONT))
    time.sleep(3)

    with canvas(virtual) as draw:
        text(draw, (0, 0), "Chann", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (32, 0), "els:", fill="white", font=proportional(SINCLAIR_FONT))
        text(draw, (64, 0), str(amount_of_channels) + ",", fill="white", font=proportional(SINCLAIR_FONT))
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

    print_sequencer(seq, sequence_length)
