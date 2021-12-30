from machine import Pin, I2C, UART
from time import sleep

from gauge import Gauge
from obd.obd import OBD


led = Pin(25, Pin.OUT)
led.value(0)

# init i2c
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100_000)

# init UART
ser = UART(0, baudrate=57600, tx=Pin(12), rx=Pin(13))

# init ELM327 (OBD reader)
obd = OBD(ser)
print(get_vin(obd))

# init 1st gauge
gauge = Gauge(i2c, 0x20, 113)
rmin = 0
rmax = 999
gauge.set_ranges([rmin, rmax], [50, 100, 150, 200, 350, 550, 650, 900])
i = rmin

while True:
    # delay
    sleep(0.01)

    # toggle led for good measure (crash indicator)
    led.toggle()

    # set 1st gauge to speed
    print('speed: ', get_speed(obd))
    gauge.set(i)


    i += 10
    if i > rmax:
        i = rmin
