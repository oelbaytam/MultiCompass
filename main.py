from machine import I2C, Pin, UART
from HMC5883L import HMC5883L
from micropyGPS import MicropyGPS
from screen import screen
from config import config

import utime
import math
    
# Define I2C bus
i2c= I2C(0, scl=Pin(13), sda=Pin(12), freq=400000)
uart = UART(0, 9600) # init with given baudrate

# Initialize Classes
HMC = HMC5883L(i2c)
gps = MicropyGPS(-5, 'dd')
screen = screen(19, 18)
activeLocation = 0

# Calibration sequence for compass
def calibrateHMC5883L():
    screen.calibrating()
    for i in range(100):
        heading = HMC.calculate_heading()
        utime.sleep(0.05)
        
def updateGPS():
    # Get GPS Data if any is recieved
    if uart.any():
        msg = uart.readline()
        #print(msg)
        if msg is not None:
            for x in msg:
                gps.update(chr(x))
    
calibrateHMC5883L()

# Main loop
while True:
    print(activeLocation)
    #print(activeLocation)
    updateGPS()
    #Print Data if updated
    heading = HMC.calculate_heading()
    screen.writeStatus(heading, config.Locations[activeLocation][0])
    #print(gps.latitude)
    utime.sleep(0.1)