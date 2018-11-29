#! /usr/bin/env python3
import os

import PyLora
from datetime import datetime

from led import led
from utils import my_logger

logger = my_logger(__name__, level="DEBUG")
root_path = os.path.dirname(os.path.abspath(__file__))

PyLora.init()
PyLora.set_frequency(433000000)
PyLora.set_tx_power(20) # 17 -> 20
PyLora.enable_crc()

if __name__ == '__main__':
    while True:
        led.on('RED')
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        logger.debug('datetime: ' + now)
        PyLora.send_packet(now.encode())
        led.off('RED')
        # sleep(1)

