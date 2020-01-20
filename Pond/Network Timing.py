##Program Creates a Average time of How long a specific WIFI attenna takes to Turn on, Load it's OS and offer web based configurations
##Hardware required: 
##Rasbery Pi
##Wifi Attena
##LANDZO 2 Channel Relay Module Expansion Board for Arduino Raspberry Pi DSP AVR PIC ARM Note: JD-VCC is 5V and VCC is 3v3, Remove jumper to accomidate this.

import socket
import RPi.GPIO as GPIO
import time
import requests
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(32,GPIO.OUT)
GPIO.output(32,GPIO.HIGH)

def boot_antenna():
    boot = True
    TIMEOUT = 130
    GPIO.output(32,GPIO.LOW)
    start = time.time()
    while boot and time.time() - start >= TIMEOUT:
        print("checking request")
        boot2 = False
        while not boot2 and time.time() - start >= TIMEOUT:
            try:
                request = requests.get('http://192.168.1.239')
                boot2 = True
            except:
                pass
        while request.status_code != 200 and time.time() - start >= TIMEOUT:
            try:
                request = requests.get('http://192.168.1.239')
            except:
                pass
            time.sleep(.10)
        boot = False
    if(not boot):
        return True
    return False
#GPIO.output(29,GPIO.LOW)
#value = boot_antenna()
#while not value:
#    print("cycle")
    #value =  boot_antenna()
        