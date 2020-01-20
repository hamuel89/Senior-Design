This repository is of the software and documents required for design 1 and design 2 at Texas State university. 

Description:
Our project upgrades a remote retention pond with new hardware and software. This includes: 
Power management, Blockchain ledger, Graphical user interface, Encryption. 

Motivation:
To reduce the risk associated with Texas quality of environmental Control stormwater runoff permit. 

Completed:
Project was completed as required by Statement of Work.

Hardware requirements:
Raspberry Pi x 2
7” LCD Display for Pi/Monitor
SleepyPi 2
LANDZO 2 Channel Relay Module Expansion Board for Arduino Raspberry Pi DSP AVR PIC ARM 
Note: JD-VCC is 5V and VCC is 3v3, remove jumper to accommodate this for Pi.

INA219 Voltage && Current Sensor
JSN-SR04T Integrated Ultrasonic Distance Sensor

Documents were summitted in the following order:
State of Work
Functional Specification
Labor Cost Schedule
D1 Poster
D2 Poster
Final Report

The Software for this project was written in both python and C. There are three portions of code written for three
different pieces of hardware had to communicate using different channels like I2C, Uart(serial), TCP. Each folder
contains the different software for each device. Simply Running Pond.py, Main.py and upload the INO file to a properly
configured Arduino with corresponding wired pins to the raspberry pi and still will function.
