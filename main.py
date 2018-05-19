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
import csv
from datetime import datetime

from ms8607 import MS8607
from as3935 import AS3935
from up501 import UP501
from time import sleep
from led import LED
import pigpio
from threading import Timer
from utils import my_logger
import os

logger = my_logger(__name__, level="DEBUG")
root_path = os.path.dirname(os.path.abspath(__file__))


def read_environment():
    ms8607 = MS8607()
    while 1:
        temperatue, pressure = ms8607.get_temperature_pressure()
        humidity = ms8607.get_humidity()
        print(
            'temperature: {} degrees Celsius, pressure: {} mbar, relative humidity: {} %RH'.format(temperatue, pressure,
                                                                                                   humidity))
        sleep(1)


def main():
    # init
    pi = pigpio.pi()
    if not pi.connected:
        print('pi is not connected by pigpio daemon')
        exit()
    led = LED(pi)
    led.all_off()
    ms8607 = MS8607()
    as3935 = AS3935(pi)

    # create observation task
    obs_path = os.path.join(root_path, 'observation')
    obs_fields = ['datetime', 'temperature', 'humidity', 'pressure', 'lightning distance']
    obs_writer = None
    obs_file = None
    os.makedirs(obs_path, exist_ok=True)

    def monitor():
        # led.on('GREEN')
        temperatue, pressure = ms8607.get_temperature_pressure()
        humidity = ms8607.get_humidity()
        distance = as3935.get_distance()
        now = datetime.now()
        data = [now.strftime('%Y%m%d%H%M%S'),temperatue, pressure, humidity, distance]
        logger(data)
        # led.off('GREEN')

        # write into file
        f_name = now.strftime('%Y%m%d') + '.csv'
        f_path = os.path.join(obs_path, f_name)
        if not os.path.exists(f_path):
            if obs_file is not None:
                obs_file.close()
            obs_file = open(f_path, 'a')
            obs_writer = csv.writer(obs_file)
            obs_writer.writerow(obs_fields)
        else:
            obs_writer.writerow(data)

        Timer(10, monitor).start()

    monitor()

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
