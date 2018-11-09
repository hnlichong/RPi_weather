#! /usr/bin/env python3
from datetime import datetime

import PyLora
from led import led
import os

from utils import my_logger

logger = my_logger(__name__, level="DEBUG")
root_path = os.path.dirname(os.path.abspath(__file__))

PyLora.init()
PyLora.set_frequency(433000000)
PyLora.enable_crc()

def csv_log_create():
    """ 创建日志文件 """
    fields = ['datetime', 'RSSI', 'SNR', 'msg']
    dir_path = os.path.join(root_path, 'lora_data')
    os.makedirs(dir_path, exist_ok=True)
    now = datetime.now()
    file_name = now.strftime('%Y%m%d') + '.csv'
    file_path = os.path.join(dir_path, file_name)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as fw:
            fw.write(','.join(fields) + '\n')
    return file_path

if __name__ == '__main__':
    # 创建日志文件
    log_file = csv_log_create()
    while True:
        PyLora.receive()   # put into receive mode
        while not PyLora.packet_available():
            # wait for a package
            led.off(u'GREEN')
        led.on(u'GREEN')
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        rssi = str(PyLora.packet_rssi())
        snr = str(PyLora.packet_snr())
        msg = PyLora.receive_packet().decode()
        data = [now, rssi, snr, msg]
        logger.debug('datetime: {}, RSSI: {}, SNR: {}, msg: {}'.format(*data))
        with open(log_file, 'a') as fa:
            fa.write(','.join(data) + '\n')

