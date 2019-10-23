# Requires Adafruit_Python_PN532

import binascii
import socket
import time
import signal
import sys
import RPi.GPIO as GPIO


import Adafruit_PN532 as PN532

RED_LED = 05
GREEN_LED = 13

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RED_LED, GPIO.OUT)
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(04, GPIO.OUT)
pwm = GPIO.PWM(04, 100)
pwm.start(5)



# PN532 configuration for a Raspberry Pi GPIO:

# GPIO 18, pin 12
CS   = 18
# GPIO 23, pin 16
MOSI = 23
# GPIO 24, pin 18
MISO = 24
# GPIO 25, pin 22
SCLK = 25

# Configure the key to use for writing to the MiFare card.  You probably don't
# need to change this from the default below unless you know your card has a
# different key associated with it.
CARD_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# Number of seconds to delay after reading data.
DELAY = 0.5

# Prefix, aka header from the card
HEADER = b'BG'

def close(signal, frame):
        sys.exit(0)

signal.signal(signal.SIGINT, close)

# Create and initialize an instance of the PN532 class
pn532 = PN532.PN532(cs=CS, sclk=SCLK, mosi=MOSI, miso=MISO)
pn532.begin()
pn532.SAM_configuration()

def readCard():
    print"Waiting For Card Input"
    while True:
        # Wait for a card to be available
        uid = pn532.read_passive_target()
        # Try again if no card found
        if uid is None:
            continue
        # Authenticate and read block 4
        if not pn532.mifare_classic_authenticate_block(uid, 4, PN532.MIFARE_CMD_AUTH_B, CARD_KEY):
            print('Failed to authenticate with card!')
            continue

        data = pn532.mifare_classic_read_block(4)
        if data is None:
            print('Failed to read data from card!')
            continue

        # Check the header
        if data[0:2] !=  HEADER:
            print('Card is not written with proper block data!')
            continue

        # Parse out the block type and subtype
        #print('User Id: {0}'.format(int(data[2:8].decode("utf-8"), 16)))
        return str(int(data[2:8].decode("utf-8"), 16))

def flash(pin):
        GPIO.output(pin, True)
        time.sleep(3)
        GPIO.output(pin, False)

def update(angle):
        duty = float(angle) / 10.0 + 2.5
        pwm.ChangeDutyCycle(duty)

def strInFile(file, str):
    with open(file) as f:
        if str in f.read():
            return True;
    return False
            
while True:
    cardId = readCard()
    if strInFile("allowed_access.txt", cardId):
        print "Access Granted"
        update(180)
        flash(GREEN_LED)
        update(0)
    else:
        print "Access Denied"
        flash(RED_LED)
    time.sleep(DELAY);
