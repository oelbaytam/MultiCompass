from machine import I2C, Pin, UART, Timer
from QMC5883L import QMC5883L
from micropyGPS import MicropyGPS
from screen import screen
from config import config
from ringLed import ringLed

import utime
import math
    
# Define I2C bus
i2c= I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
uart = UART(0, 9600) # init with given baudrate

# Initialize Classes
qmc = QMC5883L(i2c)
gps = MicropyGPS(-5, 'dd')
screen = screen(17, 16)
ring = ringLed(28)
timer = Timer()
buttonInterrupt = Pin(18, Pin.IN)
activeLocation = 0

# Calibration sequence for compass
def calibrateQMC5883L():
    screen.calibrating()
    for i in range(100):
        ring.animate(i)
        heading = qmc.calculate_heading()
        utime.sleep(0.05)
        
def updateGPS():
    # Get GPS Data if any is recieved
    if uart.any():
        msg = uart.readline()
        #print(msg)
        if msg is not None:
            for x in msg:
                gps.update(chr(x))
                
def debounce():
    timer.init(mode=Timer.ONE_SHOT, period=300, callback=rebounce)
    
def rebounce(timer):
    global buttonInterrupt
    buttonInterrupt.irq(handler=buttonPressed)
    
def buttonPressed(pin):
    print("Pressed")
    global activeLocation
    global buttonInterrupt
    buttonInterrupt.irq(handler=None)
    debounce()
    activeLocation += 1
    activeLocation = activeLocation % len(config.Locations)

    
    
calibrateQMC5883L()
buttonInterrupt.irq(trigger=Pin.IRQ_RISING, handler=buttonPressed)

# Main loop
while True:
    print(activeLocation)
    #print(activeLocation)
    updateGPS()
    #Print Data if updated
    heading = qmc.calculate_heading()
    ring.clear()
    ring.updateHeading(heading, (255, 0, 0))
    screen.writeStatus(heading, config.Locations[activeLocation][0])
    #print(gps.latitude)
    utime.sleep(0.1)