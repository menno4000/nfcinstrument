import threading
import serial
import time

SERIAL_PORT = "/dev/rfcomm0"
bluetoothSerial = serial.Serial(SERIAL_PORT, baudrate=115200, bytesize=serial.EIGHTBITS)
DATA_LENGTH = 3


def decode(string, encoding='utf-8', errors='ignore'):
    return string.decode(encoding=encoding, errors=errors)


class ReceiveInput(object):

    def __init__(self, queue):
        thread = threading.Thread(target=self.run, args=(queue, ))
        thread.daemon = True
        thread.start()

    def run(self, queue):
        global bluetoothSerial
        print("BT_INFO - Start listening for new sounds on serial '%s'" % SERIAL_PORT)
        while True:
            try:
                data = bluetoothSerial.read(size=DATA_LENGTH)
                if data and len(data) == DATA_LENGTH:
                    print("BT_INFO - Received data: %s" % decode(data))
                    queue.put(str(data, 'utf-8'))
            except serial.SerialException:
                print("BT_ERROR - No Bluetooth connection. Retrying in five seconds on serial port '%s'." % SERIAL_PORT)
                time.sleep(5)
                bluetoothSerial = serial.Serial(SERIAL_PORT, baudrate=115200, bytesize=serial.EIGHTBITS)


