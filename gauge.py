from mcp23008 import MCP23008
from s7s import S7S


class Gauge:
    def __init__(self, i2c, mcp_addr, s7s_addr):
        self.i2c = i2c

        # init mcp23008
        self.mcp = MCP23008(self.i2c, mcp_addr)
        self.mcp.set_dir(0x00)

        # init S7S
        self.s7s = S7S(self.i2c, s7s_addr)

        self.min = 0
        self.max = 9999
        self.even_led_ranges()

    def set_ranges(self, total_range, led_ranges=None):
        """Set the ranges for display.

        Args:
          total_range: 2 value tuple for the total range limits.
          led_ranges: 8 value tuple for each threshold at which to turn on
                      each LED. No value specified will divide the range evenly.
        """
        self.min = total_range[0]
        self.max = total_range[1]

        if led_ranges:
            self.led_ranges = led_ranges
        else:
            self.even_led_ranges()

    def even_led_ranges(self):
            self.led_ranges = list(range(self.min, self.max, int((self.max - self.min) / 9)))[1:]

    def set(self, value):
        # set which LEDs to turn on
        mcp_val = 0x00
        for i, x in enumerate(self.led_ranges):
            if value >= x:
                mcp_val |= 1 << i
        self.mcp.set_output(mcp_val)

        # set which value to display on the 7 segment
        self.s7s.write_int(value)
