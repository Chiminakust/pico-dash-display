

class MCP23008:
    IODIR   = 0x00
    IPOL    = 0x01
    GPINTEN = 0x02
    DEFVAL  = 0x03
    INTCON  = 0x04
    IOCON   = 0x05
    GPPU    = 0x06
    INTF    = 0x07
    INTCAP  = 0x08
    GPIO    = 0x09
    OLAT    = 0x0A

    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address

    def set_dir(self, direction):
        """8-bit direction register, 1 = input, 0 = output."""
        self.i2c_write_reg(MCP23008.IODIR, direction)

    def set_output(self, output):
        """8-bit output latches register."""
        self.i2c_write_reg(MCP23008.OLAT, output)

    def i2c_write_reg(self, reg, data):
        return self.i2c.writeto(self.address, bytes([reg, data]))
