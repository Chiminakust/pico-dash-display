

class S7S:
    CLEAR_DISPLAY      = 0x76
    DECIMAL_CONTROL    = 0x77
    CURSOR_CONTROL     = 0x79
    BRIGHTNESS_CONTROL = 0x7a
    DIGIT_1_CONTROL    = 0x7b
    DIGIT_2_CONTROL    = 0x7c
    DIGIT_3_CONTROL    = 0x7d
    DIGIT_4_CONTROL    = 0x7e
    BAUD_RATE_CONFIG   = 0x7f
    I2C_ADDRESS_CONFIG = 0x80
    FACTORY_RESET      = 0x81

    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.num_len = 0
        self.clear()

    def clear(self):
        self.i2c_write_reg(S7S.CLEAR_DISPLAY)
        
    def change_address(self, new_address):
        assert 0x01 <= new_address <= 0x7e, "new address must be in valid range"
        
        self.i2c_write_reg(S7S.I2C_ADDRESS_CONFIG, new_address)

    def write_int(self, x: int):
        num = [int(y) for y in str(x)[:4]]
        if len(num) < self.num_len:
            self.clear()
        self.num_len = len(num)

        for i, c in enumerate(reversed(num)):
            self.write_digit(c, 3 - i)

    def write_digit(self, digit, position):
        return self.i2c_write_reg(position + S7S.DIGIT_1_CONTROL, self.int_to_digit(digit))

    def int_to_digit(self, n):
        return {
            ' ': 0x00,
            0: 0x3f,
            1: 0x06,
            2: 0x5b,
            3: 0x4f,
            4: 0x66,
            5: 0x6d,
            6: 0x7d,
            7: 0x07,
            8: 0x7f,
            9: 0x6f
        }[n]

    def set_cursor(self, position):
        return self.i2c_write_reg(S7S.CURSOR_CONTROL, position)

    def i2c_write_reg(self, reg, data=None):
        if data:
            buf = bytes([reg, data])
        else:
            buf = bytes([reg])
        try:
            return self.i2c.writeto(self.address, buf)
        except OSError:
            print('could not write i2c')

    def i2c_write_buf(self, reg, buf):
        return self.i2c.writeto_mem(self.address, reg, buf)
