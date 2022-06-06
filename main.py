from machine import Pin, I2C, UART
from time import sleep

from gauge import Gauge
from elm327 import ELM327
from pca9634 import PCA9634
from s7s import S7S


led = Pin(25, Pin.OUT)
led.value(0)

# init i2c
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400_000)


# init UART
# ser = UART(0, baudrate=38400, tx=Pin(0), rx=Pin(1))


# init ELM327 (OBD reader)
# elm = ELM327(ser)
print('reset')
#elm.reset()
# print('VIN:\n', elm.get_vin())

# init gauges
gauge1 = Gauge(i2c, 0x08, 0x20)
gauge2 = Gauge(i2c, 0x10, 0x21)
gauge3 = Gauge(i2c, 0x18, 0x22)
rmin = 0
rmax = 9999
gauge1.set_ranges([rmin, rmax])
gauge2.set_ranges([rmin, rmax])
gauge3.set_ranges([rmin, rmax])
#speed = 0
i = 0
gauge1.set(1200)
gauge2.set(1200)
gauge3.set(1200)

print('init done')

while True:
    # delay
    #sleep(0.50)

    # toggle led for good measure (crash indicator)
    led.toggle()

    gauge1.set(i)
    gauge2.set(i)
    gauge3.set(i)
    

    i += 250
    if i >= rmax:
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
