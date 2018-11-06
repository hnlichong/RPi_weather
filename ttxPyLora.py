import PyLora
from datetime import datetime
from time import sleep
PyLora.init()
PyLora.set_frequency(433000000)
PyLora.set_tx_power(20) # 17 -> 20
PyLora.enable_crc()
while True:
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    msg = u'time: %s' % now
    PyLora.send_packet(msg.encode())
    print u'Packet sent: %s' % msg
    sleep(1)
