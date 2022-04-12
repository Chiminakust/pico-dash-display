from machine import Pin, I2C, UART
from time import sleep

from gauge import Gauge
from elm327 import ELM327
from pca9634 import PCA9634


led = Pin(25, Pin.OUT)
led.value(0)

# init i2c
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100_000)

# init UART
ser = UART(0, baudrate=38400, tx=Pin(0), rx=Pin(1))

# init ELM327 (OBD reader)
# elm = ELM327(ser)
print('reset')
#elm.reset()
# print('VIN:\n', elm.get_vin())

# init 1st gauge
#gauge = Gauge(i2c, 0x20, 113)
rmin = 0
rmax = 4500
#gauge.set_ranges([rmin, rmax])
#speed = 0
i = 0
#gauge.set(4500)

led_driver = PCA9634(i2c, 0x10)
states = [0] * 8

while True:
    # delay
    sleep(0.51)

    # toggle led for good measure (crash indicator)
    led.toggle()

    states = [1] * i + [0] * (8-i)
    led_driver.set_leds_states(states)

    i += 1
    if i >= 9:
        i = 0


    # set 1st gauge to speed
    #print('engine coolant temperature:', elm.get_engine_coolant_temperature(), '°C')

    #print('intake manifold pressure:', elm.get_intake_manifold_pressure(), 'kPa')

 #   rpm = elm.get_engine_rpm()
#    print('engine rpm:', rpm, 'rpm')


    #speed = elm.get_speed()

  #print('speed:', speed, 'km/h')

#     print('oil temperature:', elm.get_engine_oil_temperature(), '°C')
   # print('\n')
    #i += 100
    #if i >= 5000:
    #    i = 0;
    #gauge.set(4500)
