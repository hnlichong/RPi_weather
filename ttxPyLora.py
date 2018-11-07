#! /usr/bin/env python
# -*- coding: utf-8 -*-
import PyLora
from datetime import datetime
from time import sleep
from led import led

PyLora.init()
PyLora.set_frequency(433000000)
PyLora.set_tx_power(20) # 17 -> 20
PyLora.enable_crc()
while True:
    led.on(u'RED')
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    msg = u'time: %s' % now
    PyLora.send_packet(msg.encode())
    print u'Packet sent: %s' % msg
    sleep(0.5)
    led.off(u'RED')
    sleep(0.5)

