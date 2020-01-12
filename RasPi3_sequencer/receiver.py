import threading
import time
import serial

SERIAL_PORT = "/dev/rfcomm0"
bluetoothSerial = serial.Serial(SERIAL_PORT, baudrate=115200, bytesize=serial.EIGHTBITS)


class ReceiveInput(object):

    def __init__(self, queue):
        thread = threading.Thread(target=self.run, args=(queue, ))
        thread.daemon = True
        thread.start()

    def run(self, queue):
        print("BT_INFO - Start listening for new sounds on serial '%s'" % SERIAL_PORT)
        while True:
            data = bluetoothSerial.read(size=3)
            if data:
                print("BT_INFO - Received data: %s" % str(data, 'utf-8'))
                queue.put(str(data, 'utf-8'))
            #time.sleep(0.2)


