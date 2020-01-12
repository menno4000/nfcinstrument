#!/bin/bash

macAdress=00:18:E4:34:CF:9F

sudo systemctl start bluetooth

echo "SCRIPT_INFO - Open serial port for communication"
#sudo rfcomm connect hci0 $macAdress 1 &
sudo rfcomm bind /dev/rfcomm0 $macAdress 1

sleep 2

echo "SCRIPT_INFO - Starting sequencer script with python"
python3 main.py