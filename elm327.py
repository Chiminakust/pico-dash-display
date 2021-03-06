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


from time import sleep


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

    def reset(self):
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
        ret = self.obd_get_current_data('05')
        return decode_temperature(ret[0])

    def get_intake_manifold_pressure(self):
        ret = self.obd_get_current_data('0B')
        return decode_pressure(ret[0])

    def get_engine_rpm(self):
        ret = self.obd_get_current_data('0C')
        return decode_rpm(ret[0])

    def get_speed(self):
        ret = self.obd_get_current_data('0D')
        return decode_speed(ret[0])

    def get_engine_oil_temperature(self):
        ret = self.obd_get_current_data('5C')
        return decode_temperature(ret[0])

    def get_vin(self):
        ret = self.obd_get_vehicle_information('02')
        # TODO: parse return
        return ret

    def AT(self, atcmd):
        return self.query('AT' + atcmd)

    def OBD(self, mode, pid):
        OBD_MODES = [
            '01', # show current data
            '02', # show freeze frame data
            '03', # show diagnostics trouble codes
            '04', # clear trouble codes and stored values
            '05', # test results, oxygen sensors
            '06', # test results, non-continuously monitored
            '07', # show 'pending' trouble codes
            '08', # special control mode
            '09', # request vehicle information
            '0A'  # request permanent trouble codes
        ]
        assert mode in OBD_MODES, f'invalid mode: {mode}'

        # check how many lines to expect for the response
        # (will be None if first time using the command)
        N = self.num_lines[(mode, pid)]

        # first byte is mode
        # 2nd and 3rd bytes are parameter identification (PID)
        cmd = f'{mode} {pid}'
        if N:
            cmd += f' {N}'

        ret = self.query(cmd)

        lines = ret.split('\r')

        # remove echo (first line is always command sent)
        lines = lines[1:]

        # retrieve only important data, last 2 lines are empty and the prompt
        lines = lines[:-2]

        # update number of lines this command returns
        self.num_lines[(mode, pid)] = len(lines)

        # return a list of bytes for each line
        ret = []
        for line in lines:
            try:
                l = []
                # remove whitespace
                line = line.replace('\r', '').replace('>', '').replace(' ', '')
                # test if UNABLETOCONNECT
                if line == 'UNABLETOCONNECT':
                    raise Exception('Car not connected')
                # read ever set of 2 ascii chars as an 8-bit hex number
                for i in range(0, len(line), 2):
                    l += [int(line[i:i + 2], 16)]

                ret += [bytes(l)]
            except ValueError:
                print("Could not convert line:", line)

        return ret

    def obd_get_current_data(self, pid):
        return self.OBD('01', pid)

    def obd_get_vehicle_information(self, pid):
        return self.OBD('09', pid)

    def query(self, cmd, EOM='\r\r>'):
        self.send(cmd)
        return self.read_until(EOM)

    def send(self, cmd):
        self.write(cmd + '\r')

    def write(self, cmd):
        self.uart.write(cmd.encode())

    def read_until(self, EOM):
        ret = ''
        n = len(EOM)

        while ret[-n:] != EOM:
            while self.uart.any() == 0:
                sleep(0.01)
            d = self.uart.read()
            try:
                ret += d.decode()
            except UnicodeError:
                print("uart decode error")

        return ret
