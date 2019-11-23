#!/bin/bash

macAdress=98:D3:31:F5:A3:3D

# install packages
#sudo apt-get update
#sudo apt-get install bluetooth bluez pi-bluetooth blueman

sudo systemctl start bluetooth

# pair with hc05
#echo "Connecting to device"
#coproc sudo bluetoothctl
#echo -e 'agent on\n' >&${COPROC[1]}
#agent on
#echo -e 'default-agent\n' >&${COPROC[1]}
#default-agent
#echo -e 'pair $macAdress\n' >&${COPROC[1]}
#output=$(cat <&${COPROC[0]})
#pair $macAdress
#echo -e 'trust $macAdress\n' >&${COPROC[1]}
#trust $macAdress
#echo -e 'exit' >&${COPROC[1]}
#exit

echo "open serial port for communication"
# open serial port
sudo rfcomm connect hci0 $macAdress 1 &

sleep 5

echo "starting sequencer script with python"
# start python script
python main.py