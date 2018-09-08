import PyLora
import time
PyLora.init()
PyLora.set_frequency(433000000)
PyLora.enable_crc()
from led import LED
import pigpio

pi = pigpio.pi()
if not pi.connected:
    print(u'pi is not connected by pigpio daemon')
    exit()
led = LED(pi)
led.on(u'RED')
time.sleep(1)
led.on(u'YELLOW')
time.sleep(1)
led.on(u'GREEN')
led.all_off()

while True:
    PyLora.receive()   # put into receive mode
    while not PyLora.packet_available():
        # wait for a package
        led.off(u'RED')
        time.sleep(0)
    rec = PyLora.receive_packet()
    print u'Packet received: {}'.format(rec)
    led.on(u'RED')

