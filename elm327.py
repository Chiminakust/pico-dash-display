"""Basic ELM327 interface for my needs.

TODO: elm327 returns means incomplete command, syntax error or invalid hex messages
TODO: method for obd commands
TODO: methods to get real time rpm, boost, speed, engine temp, etc
TODO: repeating previous command by sending only '\r'
TODO: there may be extra 0x00 chars inserted in the input data, remove them
TODO: read battery voltage
TODO: handle multiline responses (datasheet p. 42)
TODO: handle when number of response lines is known
TODO: AT MA command to put in monitor all mode, any char sent after will stop the mode
"""


# utils functions
def bytes_to_int(bs):
    """ converts a big-endian byte array into a single integer """
    v = 0
    p = 0
    for b in reversed(bs):
        v += b * (2 ** p)
        p += 8
    return v


def decode_temperature(message):
    """Temperature is in the -40:215 celsius range as int."""

    return  bytes_to_int(message[2:]) - 40

def decode_pressure(message):
    """Pressure is in the 0:255 kPa range as int."""

    return int(message[2])

def decode_percent(message):
    """Percent is in the 0:100 range as float."""

    return int(message[2]) * 100.0 / 255.0

def decode_rpm(message):
    """RPM is in the 0:16384 revs/min range as int."""

    return bytes_to_int(message[2:]) / 4

def decode_speed(message):
    """Speed is in the 0:255 km/h range as int."""

    return int(message[2])


class ELM327:
    def __init__(self, uart):
        """Init the ELM327.

        Args:
          uart: A preinitialized UART bus for the RP2 pico board.
        """

        self.uart = uart

        # Dict of number of expected lines for each supported command.
        # Will be updated by the functions calling it.
        # Each entry is in the format:
        # (mode, pid): lines
        self.num_lines = {
            ('01', '05'): None, # engine coolant temperature
            ('01', '0B'): None, # intake manifold pressure
            ('01', '0C'): None, # engine rpm
            ('01', '0D'): None, # vehicle speed
            ('01', '11'): None, # throttle position
            ('01', '5C'): None, # engine oil temperature
            ('09', '02'): None, # VIN
        }

    def led_test(self):
        """Simple test to make the LEDs on the ELM327 flash in sequence."""

        return self.AT('Z')

    def read_battery_voltage(self):
        """Read the voltage at the car's battery."""

        return self.AT('RV')

    def search_protocol(self):
        return self.set_protocol('0')

    def set_protocol(self, protocol):
        return self.AT(f'SP {protocol}')

    def get_engine_coolant_temperature(self):
        ret = obd_get_current_data('05')
        # TODO: temperature is 3rd byte as decimal - 40 in Celsius
        return ret

    def get_intake_manifold_pressure(self):
        ret = obd_get_current_data('0B')
        # TODO decode
        print('intake manifold pressure = ', decode_pressure(ret), 'kPa')
        return ret

    def get_engine_rpm(self):
        ret = obd_get_current_data('0C')
        # TODO: rpm is the last 2 bytes / 4
        return ret

    def get_speed(self):
        ret = obd_get_current_data('0D')
        # TODO: parse speed
        return ret

    def get_engine_oil_temperature(self):
        ret = obd_get_current_data('5C')
        # TODO: parse oil temp
        return ret

    def get_vin(self):
        ret = obd_get_vehicle_information('02')
        # TODO: parse return
        return ret

    def AT(self, atcmd):
        return self.query('AT' + atcmd)

    def OBD(self, mode, pid):
        OBD_MODES = [
            0x01, # show current data
            0x02, # show freeze frame data
            0x03, # show diagnostics trouble codes
            0x04, # clear trouble codes and stored values
            0x05, # test results, oxygen sensors
            0x06, # test results, non-continuously monitored
            0x07, # show 'pending' trouble codes
            0x08, # special control mode
            0x09, # request vehicle information
            0x0A  # request permanent trouble codes
        ]
        assert mode in OBD_MODES, f'invalid mode: {mode}'

        # check how many lines to expect for the response
        # (will be None if first time using the command)
        lines = self.num_lines[(mode, pid)]

        # first byte is mode
        # 2nd and 3rd bytes are parameter identification (PID)
        cmd = f'{mode} {pid}'
        if lines:
            cmd += f' {lines}'

        ret = self.query(cmd)

        # TODO: update lines
        # self.num_lines[(mode, pid)] = lines

        return ret

    def obd_get_current_data(self, pid):
        return self.OBD('01', pid)

    def obd_get_vehicle_information(self, pid):
        return self.OBD('09', pid)

    def query(self, cmd):
        self.send(cmd)
        # TODO: read, parse and return response
        return 0

    def send(self, cmd):
        self.write(cmd + '\r')

    def write(self, cmd):
        self.uart.write(cmd.encode()))
