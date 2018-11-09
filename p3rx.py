#! /usr/bin/env python3
import PyLora
from led import led

PyLora.init()
PyLora.set_frequency(433000000)
PyLora.enable_crc()

while True:
    PyLora.receive()   # put into receive mode
    while not PyLora.packet_available():
        # wait for a package
        led.off(u'GREEN')
    pkt = PyLora.receive_packet()
    rssi = PyLora.packet_rssi()
    snr = PyLora.packet_snr()
    msg = u'packet: {} \nRSSI: {}, SNR: {}\n' .format(pkt, rssi, snr)
    print msg
    led.on(u'GREEN')
    fo = open('./lora_data/rx', 'a')
    fo.write(msg)
    fo.close()

