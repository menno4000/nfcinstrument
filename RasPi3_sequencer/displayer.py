import time

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

# create matrix device
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=16, block_orientation=-90, rotate=0)
#deviceText = max7219(serial, cascaded=None, block_orientation=-90, rotate=0)


def print_sequencer(sequencer):
    if len(sequencer[0]) > 32:
        print("ERROR - Can't show sequence lengths longer then 32.")
        return
    with canvas(device) as draw:
        for y in range(len(sequencer)):
            if y < 3:
                print(sequencer[y])
                for x in range(len(sequencer[y])):
                    if sequencer[y][x] == 1:
                        point = x, y
                        draw.point(point, fill="white")