from machine import I2C
import utime
import math
from config import config  # You should define config.Declination in degrees

class HMC5883L:
    # HMC5883L default I2C address
    ADDRESS = 0x1E

    # Register addresses
    REG_CONFIG_A = 0x00
    REG_CONFIG_B = 0x01
    REG_MODE     = 0x02
    REG_DATA_X_MSB = 0x03
    REG_STATUS   = 0x09

    def __init__(self, i2c: I2C):
        self.i2c = i2c
        self._initialize_sensor()

        self.xlow = 32767
        self.xhigh = -32768
        self.ylow = 32767
        self.yhigh = -32768

    def _initialize_sensor(self):
        # Configuration Register A: 8-average, 15 Hz default, normal measurement
        self.i2c.writeto_mem(self.ADDRESS, self.REG_CONFIG_A, b'\x70')  # 0b01110000

        # Configuration Register B: Gain = 1.3 Ga (default)
        self.i2c.writeto_mem(self.ADDRESS, self.REG_CONFIG_B, b'\x20')  # 0b00100000

        # Mode register: Continuous measurement mode
        self.i2c.writeto_mem(self.ADDRESS, self.REG_MODE, b'\x00')
        utime.sleep_ms(100)

    def _read_raw_data(self):
        data = self.i2c.readfrom_mem(self.ADDRESS, self.REG_DATA_X_MSB, 6)
        x = _to_signed(int.from_bytes(data[0:2], 'big'))
        z = _to_signed(int.from_bytes(data[2:4], 'big'))
        y = _to_signed(int.from_bytes(data[4:6], 'big'))
        return x, y, z

    def read_calibrated_data(self):
        x, y, _ = self._read_raw_data()

        # Track min/max for calibration
        if x < self.xlow: self.xlow = x
        if x > self.xhigh: self.xhigh = x
        if y < self.ylow: self.ylow = y
        if y > self.yhigh: self.yhigh = y

        if self.xlow == self.xhigh or self.ylow == self.yhigh:
            return None  # not enough calibration data yet

        # Center
        x -= (self.xhigh + self.xlow) / 2
        y -= (self.yhigh + self.ylow) / 2

        # Normalize
        fx = float(x) / (self.xhigh - self.xlow)
        fy = float(y) / (self.yhigh - self.ylow)

        return fx, fy

    def calculate_heading(self):
        calibrated = self.read_calibrated_data()
        if calibrated is None:
            return None

        fx, fy = calibrated

        heading = math.degrees(math.atan2(fy, fx)) + config.Declination

        if heading < 0:
            heading += 360
        elif heading >= 360:
            heading -= 360

        return heading
    
def _to_signed(val):
    return val - 65536 if val > 32767 else val

