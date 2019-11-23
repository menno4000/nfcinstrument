import threading

import pygame
import serial

bluetoothSerial = serial.Serial("/dev/rfcomm0", baudrate=115200, bytesize=serial.EIGHTBITS)


class ReceiveInput(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, interval=0.01):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        print("INFO - Start listening for new sounds.")
        thread.start()

        #pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=2 ** 12)
        #self.channel = pygame.mixer.Channel(0)
        #self.sound = pygame.mixer.Sound('./sounds/Aubit_Kick5.wav')

    def run(self):
        """ Method that runs forever """
        while True:
            data = bluetoothSerial.read(size=5)
            if data:
                print(data)
                self.channel.play(self.sound)
                # time.sleep(1)
            # bluetoothSerial.write("Message in parallel thread while playing...")
