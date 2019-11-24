# nfc instrument

## Arduino racket
We are using an Arduino NANO with the bluetooth HC05 and an NFC Shield as a racket. 
The racket can read notes from RFID chips and send them via bluetooth to the Raspberry Pi. 

## Raspberry Pi 3 - Sequencer, Bluetooth receiver & Displayer
The Pi receives signals from the Arduino and start a Sequencer. 
It will add noted to different channels and start playing them sequentially.

### Displayer
For visual support we will use a already existing LED matrix (16 x MAX7219). 
It will show the programmed sequence and give additional information.

### Setup

Connect your pins from the MAX7219 Matrix to the raspberry according to the following images:

'pictures'

install packages on RasPi:
```
sudo apt-get update

# get Bluetooth setup
sudo apt-get install bluetooth bluez pi-bluetooth blueman

# get python3 and pip3
sudo apt-get install python3-dev libffi-dev libssl-dev -y.
wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz.
tar xJf Python-3.6.3.tar.xz.
cd Python-3.6.3.
./ configure.
make.
sudo make install.
sudo pip3 install --upgrade pip.

# install dependencies for LED_Matrix
pip3 install luma.core luma.led_matrix
```

To establish a connection between the RasPi and Arduino (via Bluetooth module HC05) execute the following commands on RasPi:
```
# pair with hc05
sudo bluetoothctl
    agent on
    default-agent
    pair $macAdress
    trust $macAdress
    exit
```

Use the following script to open serial port to receive bluetooth signals in python and start the sequencer:

```./RasPi3_sequencer/startup_nfc_instrument.sh```