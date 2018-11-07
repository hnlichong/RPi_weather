#! /usr/bin/env python
# -*- coding: utf-8 -*-
import PyLora
import time
from led import led

PyLora.init()
PyLora.set_frequency(433000000)
PyLora.enable_crc()

while True:
    PyLora.receive()   # put into receive mode
    while not PyLora.packet_available():
        # wait for a package
        led.off(u'GREEN')
        time.sleep(0)
    pkt = PyLora.receive_packet()
    rssi = PyLora.packet_rssi()
    snr = PyLora.packet_snr()
    msg = u'packet: {} \nRSSI: {}, SNR: {}\n' .format(pkt, rssi, snr)
    print msg
    led.on(u'GREEN')
    fo = open('./lora_data/rx', 'a')
    fo.write(msg)
    fo.close()

