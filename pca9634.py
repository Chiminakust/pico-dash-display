"""

First byte  = I2C slave address
Second byte = Control register:
              1b = auto-increment flag
              2b = auto-increment options
              5b = register address
"""


# Register definitions


class PCA9634:
    # registers
    MODE1      = 0x00
    MODE2      = 0x01
    PWM0       = 0x02
    PWM1       = 0x03
    PWM2       = 0x04
    PWM3       = 0x05
    PWM4       = 0x06
    PWM5       = 0x07
    PWM6       = 0x08
    PWM7       = 0x09
    GRPPWM     = 0x0A
    GRPFREQ    = 0x0B
    LEDOUT0    = 0x0C
    LEDOUT1    = 0x0D
    SUBADR1    = 0x0E
    SUBADR2    = 0x0F
    SUBADR3    = 0x10
    ALLCALLADR = 0x11
    # flags
    AUTOINC    = 0x80

    def __init__(self, i2c, address: int, brightness: int=0x5):
        self.i2c = i2c
        self.address = address
        self.configure()
        self.set_brightness(brightness)
        self.set_leds_states()

    def i2c_write_reg(self, reg, data):
        return self.i2c.writeto(self.address, bytes([reg, data]))

    def i2c_write_autoincrement(self, reg, data):
        return self.i2c.writeto(self.address, bytes([reg | PCA9634.AUTOINC] + list(data)))

    def configure(self):
        self.i2c_write_reg(PCA9634.MODE1, 0x00)
        self.i2c_write_reg(PCA9634.MODE2, 0x05)

    def set_brightness(self, brightness: int):
        assert 0 <= brightness <= 0xff, f'brightness must be 8 bit value'
        self.brightness = brightness
        self.i2c_write_reg(PCA9634.GRPPWM, self.brightness)

    def set_leds_states(self, states: list=[0]*8):
        x = 0

        for i, state in enumerate(states):
            z = 3 if state else 0
            x |= z << (2 * i)

        return self.i2c_write_autoincrement(PCA9634.LEDOUT0, x.to_bytes(2, 'little'))
