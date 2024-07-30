from machine import Pin, I2C
import ssd1306

class screen:    
    
    def __init__(self, scl, sda):
        self.i2c = I2C(0, scl=Pin(scl), sda=Pin(sda)) 			# Initialize I2C with corresponding pins
        self.display = ssd1306.SSD1306_I2C(128, 32, self.i2c) 	# Initialize Display
        self.display.fill_rect(0, 0, 128, 64, 0) 				# Clear Screen
        
    def writeStatus(self, heading, location):
        self.display.fill_rect(0, 0, 128, 27, 0)
        self.display.text(f'Towards {location}', 0, 0, 1)
        self.display.text(f'Heading: {heading}', 0, 9, 1)
        self.display.show()
        return None

    def timeSinceFix(self, fix):
        self.display.fill_rect(0, 18, 128, 36, 0)
        if fix:
            self.display.text(f'Last fix: {fix}s',0,18,1)
        else:
            self.display.text(f'No gps fix available',0,18,1)
        self.display.show()
    
    def calibrating(self):
        self.display.text(f'Calibrating', 23, 9, 1)
        self.display.text(f'Move in circles', 4, 18, 1)
        self.display.show()