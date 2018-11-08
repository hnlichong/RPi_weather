#! /usr/bin/env python3
import csv
from datetime import datetime

from ms8607 import ms8607
from as3935 import as3935
from up501 import up501
from time import sleep
from led import led
from utils import my_logger
import os

logger = my_logger(__name__, level="DEBUG")
root_path = os.path.dirname(os.path.abspath(__file__))


def read_environment():
    while 1:
        temperatue, pressure = ms8607.get_temperature_pressure()
        humidity = ms8607.get_humidity()
        print(
            'temperature: {} degrees Celsius, pressure: {} mbar, relative humidity: {} %RH'.format(temperatue, pressure,
                                                                                                   humidity))
        sleep(1)

def append_data_to_file(data, row_fields, path, now = datetime.now()):
    f_name = now.strftime('%Y%m%d') + '.csv'
    f_path = os.path.join(path, f_name)
    if not os.path.exists(f_path):
        with open(f_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row_fields)
            writer.writerow(data)
    else:
        with open(f_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data)


def main():
    # 系统启动后黄灯亮
    led.on('YELLOW')

    # create observation task
    env_path = os.path.join(root_path, 'env_data')
    env_fields = ['datetime', 'temperature(℃)', 'humidity(%)', 'pressure(mbar)']
    lightning_path = os.path.join(root_path, 'lightning_data')
    lightning_fields = ['datetime', 'events', 'distance(KM)']
    os.makedirs(env_path, exist_ok=True)
    os.makedirs(lightning_path, exist_ok=True)

    def env_monitor():
        # nonlocal env_path, env_fields
        temperatue, pressure = ms8607.get_temperature_pressure()
        humidity = ms8607.get_humidity()
        now = datetime.now()
        data = [now.strftime('%Y%m%d%H%M%S'), temperatue, humidity, pressure]
        logger.debug(data)
        # write into file
        append_data_to_file(data, env_fields, env_path, now)

    def lightning_monitor():
        distance = as3935.get_distance()
        events = as3935.get_INT()
        now = datetime.now()
        data = [now.strftime('%Y%m%d%H%M%S'), events, distance]
        logger.debug(data)
        # write into file
        append_data_to_file(data, lightning_fields, lightning_path, now)

    while False:
        env_monitor()
        lightning_monitor()
        sleep(60)
        pass

    while True:
        up501.read()
        sleep(5)

    # stop pi
    pi.stop()



if __name__ == '__main__':
    main()
