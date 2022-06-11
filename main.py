from machine import Pin, I2C, UART
from time import sleep

from gauge import Gauge
from elm327 import ELM327
from pca9634 import PCA9634
from s7s import S7S


# init status LED (on-board LED on the Raspberry Pi Pico)
led = Pin(25, Pin.OUT)
led.value(0)

# init i2c
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400_000)

# init UART (connector is GND TX RX VDD)
ser = UART(0, baudrate=38400, tx=Pin(0), rx=Pin(1))

# init ELM327 (OBD reader)
elm = ELM327(ser)
elm.reset()
print('ELM reset done')

# print('VIN:\n', elm.get_vin())

# uncomment in case a S7S' address has reset
#tmp = S7S(i2c, 0x71)
#tmp.change_address(0x21)

# init gauges
gauge_speed = Gauge(i2c, 0x08, 0x21)
gauge_rpm = Gauge(i2c, 0x18, 0x22)
gauge_intake_p = Gauge(i2c, 0x10, 0x20)

# set min and max display values
gauge_speed.set_ranges([0, 130])    # in km/h
gauge_rpm.set_ranges([0, 6000])     # in rpm
gauge_intake_p.set_ranges([0, 200]) # in KPa

speed = 999
rpm = 9999
pressure = 999
gauge_speed.set(speed)
gauge_rpm.set(rpm)
gauge_intake_p.set(pressure)

print('init done')

while True:
    # toggle led for good measure (crash indicator)
    led.toggle()
    
    try:
        speed = int(elm.get_speed())
        rpm = int(elm.get_engine_rpm())
        pressure = int(elm.get_intake_manifold_pressure())
    except Exception:
        sleep(0.5)


    gauge_speed.set(speed)
    gauge_rpm.set(rpm)
    gauge_intake_p.set(pressure)
