from time import sleep
import pigpio
import pynmea2
from utils import my_logger

logger = my_logger(__name__)

class UP501(object):
    PPS = 22
    RXD = 14
    TXD = 15

    def __init__(self, pi):
        self.pi = pi
        self.pi.set_mode(UP501.PPS, pigpio.INPUT)
        self.pi.set_mode(UP501.TXD, pigpio.INPUT)
        self.pi.set_mode(UP501.RXD, pigpio.OUTPUT)

    def read(self):
        status = self.pi.bb_serial_read_open(UP501.TXD, 9600, 8)
        while True:
            (count, data) = self.pi.bb_serial_read(UP501.TXD)
            sleep(1)
            if count > 0:
                break
        self.pi.bb_serial_read_close(UP501.TXD)
        res = ''
        try:
            res = data.decode()
        except:
            pass
        logger.debug(res)
        return res

    def parse(self):
        ret = []
        lines = self.read().splitlines()
        for line in lines:
            res = None
            try:
                res = pynmea2.parse(line)
            except:
                pass
            ret.append(res)
            logger.debug(res)
        return ret


# 单例模式
pi = pigpio.pi()
if not pi.connected:
    print('pi is not connected by pigpio daemon')
    exit()
up501 = UP501(pi)


