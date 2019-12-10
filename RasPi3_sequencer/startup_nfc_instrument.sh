#!/bin/bash

macAdress=98:D3:31:F5:A3:3D

sudo systemctl start bluetooth

echo "open serial port for communication"
# open serial port
sudo rfcomm connect hci0 $macAdress 1 &

sleep 5

echo "starting sequencer script with python"
# start python script
python3 main.py