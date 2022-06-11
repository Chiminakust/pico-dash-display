from pca9634 import PCA9634
from s7s import S7S


class Gauge:
    def __init__(self, i2c, pca_addr, s7s_addr):
        self.i2c = i2c

        # init pca9634
        self.pca = PCA9634(self.i2c, pca_addr)

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
        print("led ranges are:", self.led_ranges)

    def even_led_ranges(self):
            step = int((self.max - self.min) / 8)
            self.led_ranges = [i * step for i in range(9)][1:]

    def set(self, value):
        # set which LEDs to turn on
        pca_states = [0] * 8
        for i, x in enumerate(self.led_ranges):
            if value >= x:
                pca_states[i] = 1
        self.pca.set_leds_states(pca_states)

        # set which value to display on the 7 segment
        self.s7s.write_int(value)
