"""
CODING STRUCTURE
import pigpio

# init pigpio
pi = pigpio.pi()
if not pi.connected:
    print('pi is not connected by pigpio daemon')
    exit()

# main functions, instancing classes...

# stop pi
pi.stop()
"""
from ms8607 import MS8607
from as3935 import AS3935
from up501 import UP501
from time import sleep
from led import LED
import pigpio


def read_environment():
    ms8607 = MS8607()
    while 1:
        temperatue, pressure = ms8607.get_temperature_pressure()
        humidity = ms8607.get_humidity()
        print('temperature: {} degrees Celsius, pressure: {} mbar, relative humidity: {} %RH'.format(temperatue, pressure, humidity))
        sleep(1)

def read_lightning(pi):
    as3935 = AS3935(pi)

def test_LED(pi):
    led = LED(pi)
    led.all_off()

def main():
    # init pigpio
    pi = pigpio.pi()
    if not pi.connected:
        print('pi is not connected by pigpio daemon')
        exit()

    # main functions, instancing classes...
    read_lightning(pi)
    while 1:
        pass

    # up501 = UP501(pi)
    # up501.get_GPS()
    # while 1:
    #     res = up501.bb()
    #     print('res {}'.format(res))

    # stop pi
    pi.stop()


main()
