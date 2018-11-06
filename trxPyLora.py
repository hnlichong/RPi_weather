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
    rec = PyLora.receive_packet()
    rssi = PyLora.packet_rssi()
    snr = PyLora.packet_snr()
    print u'Packet received: {}'.format(rec)
    print u'RSSI: {}, SNR: {}'.format(rssi, snr)
    led.on(u'GREEN')

