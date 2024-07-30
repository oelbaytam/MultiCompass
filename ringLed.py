from machine import Pin
import utime
import neopixel
import math

class ringLed:
    
    def __init__(self, di):
        pin = Pin(di)
        self.n = neopixel.NeoPixel(pin, 16)
        
    def updateHeading(self, heading, color):
        indexLed = math.floor(heading/22.5)
        self.n.__setitem__(indexLed, color)
        self.n.write()
    
    def clear(self):
        for i in range(16):
            self.n[i] = (0, 0, 0)
        self.n.write()
        
    def animate(self, offset):
        for i in range(16):
            self.n[i] = (((i+offset)%16) * 16, 0, 0)
        self.n.write()
    
    
        