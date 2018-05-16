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
        self.pi.bb_serial_read_close(UP501.TXD)
        
    def bb(self):
        status = self.pi.bb_serial_read_open(UP501.TXD, 9600, 8)
        while 1:
            (count, data) = self.pi.bb_serial_read(UP501.TXD)
            sleep(1)
            if count > 0:
                break
        res = data.decode()
        res = data
        logger.debug('bb serial read {}'.format(res))
        self.pi.bb_serial_read_close(UP501.TXD)
        return res

    def get_GPS(self):
        res = self.bb()
        lines = res.splitlines()
        for line in lines:
            msg = pynmea2.parse(line)
            logger.debug(msg)
            # import pdb; pdb.set_trace()
            # if msg.is_valid:




