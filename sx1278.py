#! /usr/bin/env python3
import PyLora

# init
PyLora.init()
PyLora.set_frequency(433000000)
PyLora.set_tx_power(20) # 17 -> 20, 最大发射功率
PyLora.enable_crc()
# export
sx1278 = PyLora
sx1278.send_str = lambda s: PyLora.send_packet(s.encode())

"""
Example:
from datetime import datetime
from time import sleep
from led import led

while True:
    led.on('RED')
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    msg = 'time: %s' % now
    PyLora.send_packet(msg.encode())
    print('Packet send: %s' % msg)
    led.off('RED')
    sleep(1)
"""


