from machine import I2C, Pin
from config import config
import utime
import math


class QMC5883L:
    # Constants
    QMC5883L_ADDRESS = 0x0D 
    QMC5883L_XOUT_LSB = 0x00 
    QMC5883L_CONTROL_1 = 0x09 
    QMC5883L_SET_RESET = 0x0B
    
    # Variables
    targetLocation = []
    

    def __init__(self, i2c):
        self.i2c = i2c
        self.init_sensor()
        self.xlow = self.xhigh = self.ylow = self.yhigh = 0

    def init_sensor(self):
        # Continuous measurement mode, output data rate = 200Hz, full scale = 8G, oversampling = 512
        self.i2c.writeto_mem(self.QMC5883L_ADDRESS, self.QMC5883L_CONTROL_1, b'\x61')
        self.i2c.writeto_mem(self.QMC5883L_ADDRESS, self.QMC5883L_SET_RESET, b'\x01')
        utime.sleep_ms(100)

    def read_raw_data(self):
        data = self.i2c.readfrom_mem(self.QMC5883L_ADDRESS, self.QMC5883L_XOUT_LSB, 6)
        x = int.from_bytes(data[0:2], 'little')
        y = int.from_bytes(data[2:4], 'little')
        z = int.from_bytes(data[4:6], 'little')
        
        # Convert to signed 16-bit
        if x >= 32768:
            x -= 65536
        if y >= 32768:
            y -= 65536
        if z >= 32768:
            z -= 65536

        return x, y, z
    
    def read_calibrated_data(self):
        x, y, z = self.read_raw_data()

        if x < self.xlow: self.xlow = x
        if x > self.xhigh: self.xhigh = x
        if y < self.ylow: self.ylow = y
        if y > self.yhigh: self.yhigh = y

        # Bail out if not enough data is available. 

        if self.xlow == self.xhigh or self.ylow == self.yhigh: return None

        # Recenter the measurement by subtracting the average 

        x -= (self.xhigh+self.xlow)/2
        y -= (self.yhigh+self.ylow)/2

        # Rescale the measurement to the range observed. 

        fx = float(x)/(self.xhigh - self.xlow)
        fy = float(y)/(self.yhigh - self.ylow)
        
        return fx, fy

    def calculate_heading(self):
        fx, fy = self.read_calibrated_data()

        heading = 180.0*math.atan2(fy,fx)/math.pi
        heading = int(heading + config.Declination)
        
        if heading<=0: heading += 360
        # Debugging: Print raw values
        return heading
