#! /usr/bin/env python3
import os

import PyLora
from datetime import datetime
from time import sleep

from ms8607 import ms8607
from led import led
from utils import my_logger

logger = my_logger(__name__, level="DEBUG")
root_path = os.path.dirname(os.path.abspath(__file__))

PyLora.init()
PyLora.set_frequency(433000000)
PyLora.set_tx_power(20) # 17 -> 20
PyLora.enable_crc()

def csv_log_create():
    """ 创建日志文件 """
    fields = ['datetime', 'temperatue', 'humidity', 'pressure']
    dir_path = os.path.join(root_path, 'lora_data')
    os.makedirs(dir_path, exist_ok=True)
    now = datetime.now()
    file_name = now.strftime('%Y%m%d') + '_tx.csv'
    file_path = os.path.join(dir_path, file_name)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as fw:
            fw.write(','.join(fields) + '\n')
    return file_path

if __name__ == '__main__':
    # 创建日志文件
    log_file = csv_log_create()
    while True:
        led.on('RED')
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        temperatue, pressure = ms8607.get_temperature_pressure()
        humidity = ms8607.get_humidity()
        data = [str(x) for x in [now, temperatue, humidity, pressure]]
        logger.debug('datetime: {}, temperatue: {}, humidity: {}, pressure: {}'.format(*data))
        msg = ','.join(data) + '\n'
        with open(log_file, 'a') as fa:
            fa.write(msg)
        PyLora.send_packet(msg.encode())
        led.off('RED')
        # sleep(1)

