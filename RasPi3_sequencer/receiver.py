import threading
import time
import serial

SERIAL_PORT = "/dev/rfcomm0"
#bluetoothSerial = serial.Serial(SERIAL_PORT, baudrate=115200, bytesize=serial.EIGHTBITS)


class ReceiveInput(object):

    def __init__(self, queue):
        thread = threading.Thread(target=self.run, args=(queue, ))
        thread.daemon = True
        print("BT_INFO - Start listening for new sounds on serial '%s'" % SERIAL_PORT)
        thread.start()

    # listening for arduino signals
    def run(self, queue):

        # example signal mocking: add kick roll
        #time.sleep(7.8)
        #print("BT_INFO - adding kick roll_part1")
        #queue.put("0")
#
        #time.sleep(7.8)
        #print("BT_INFO - adding kick roll_part2")
        #queue.put("0")
        #time.sleep(0.25)
        #queue.put("0")

        while True:
            #data = bluetoothSerial.read(size=5)
            #if data:
            #    print("BT_INFO - Received data: %s" % data)
            #    queue.put("2")
            print("hello")


