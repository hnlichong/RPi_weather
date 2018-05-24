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
    env_path = os.path.join(root_path, 'env_data')
    env_fields = ['datetime', 'temperature(℃)', 'humidity(%)', 'pressure(mbar)']
    lightning_path = os.path.join(root_path, 'lightning_data')
    lightning_fields = ['datetime', 'events', 'distance(KM)']
    os.makedirs(env_path, exist_ok=True)
    os.makedirs(lightning_path, exist_ok=True)

    def env_monitor(time):
        # nonlocal env_path, env_fields
        # led.on('GREEN')
        temperatue, pressure = ms8607.get_temperature_pressure()
        humidity = ms8607.get_humidity()
        now = datetime.now()
        data = [now.strftime('%Y%m%d%H%M%S'), temperatue, humidity, pressure]
        logger.debug(data)
        # led.off('GREEN')

        # write into file
        f_name = now.strftime('%Y%m%d') + '.csv'
        f_path = os.path.join(env_path, f_name)
        if not os.path.exists(f_path):
            with open(f_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(env_fields)
                writer.writerow(data)
        else:
            with open(f_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(data)
        Timer(time, env_monitor, [time]).start()

    def lightning_monitor(time):
        distance = as3935.get_distance()
        events = as3935.get_INT()
        now = datetime.now()
        data = [now.strftime('%Y%m%d%H%M%S'), events, distance]
        logger.debug(data)
        # led.off('GREEN')

        # write into file
        f_name = now.strftime('%Y%m%d') + '.csv'
        f_path = os.path.join(lightning_path, f_name)
        if not os.path.exists(f_path):
            with open(f_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(lightning_fields)
                writer.writerow(data)
        else:
            with open(f_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(data)
        Timer(time, lightning_monitor, [time]).start()

    env_monitor(60)
    lightning_monitor(1)

    while 1:
        pass

    # up501 = UP501(pi)
    # up501.get_GPS()
    # while 1:
    #     res = up501.bb()
    #     print('res {}'.format(res))

    # stop pi
    pi.stop()


if __name__ == '__main__':
    main()
