import PyLora
import time
PyLora.init()
PyLora.set_frequency(433000000)
PyLora.enable_crc()
while True:
    msg = u'time: %s' % time.time()
    PyLora.send_packet(msg.encode())
    print u'Packet sent: %s' % msg
    time.sleep(1)
