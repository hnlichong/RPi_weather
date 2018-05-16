from time import sleep, time
import pigpio
from utils import bytes_to_hex_str
from led import LED
from utils import my_logger

logger = my_logger(__name__, level="DEBUG")

class AS3935(object):
    CE = 16
    MISO = 19
    MOSI = 20
    SCLK = 21
    IRQ = 12

    def __init__(self, pi):
        self.pi = pi
        self.led = LED(self.pi)
        self.led.all_on()
        
        # init SPI with mode 1, 10 KHz
        try:
            self.pi.bb_spi_open(AS3935.CE, AS3935.MISO, AS3935.MOSI, AS3935.SCLK, 10000, 1)
        except pigpio.error as e:
            if e.value == 'GPIO already in use':
                self.pi.bb_spi_close(AS3935.CE)        
                self.pi.bb_spi_open(AS3935.CE, AS3935.MISO, AS3935.MOSI, AS3935.SCLK, 10000, 1)
                
        # Sets all registers in default mode
        self.write(0x3C, 0x96)
        sleep(1)
        self.led.all_off()

        # choose occasion
        self.set_indoor()

        # Antenna Tuning
        self.tunning()

        # init IRQ for interrupts
        # set IRQ pull down as default status, as IRQ goes high for interrupts
        self.pi.set_pull_up_down(AS3935.IRQ, pigpio.PUD_DOWN)

        # init lightning interrupt
        self.int = self.pi.callback(
            AS3935.IRQ, pigpio.RISING_EDGE, self._cb_int)

    
    def __del__(self):
        self.pi.bb_spi_close(AS3935.CE)        

    def _cb_int(self, gpio, level, tick):
        # read interrupt resigter to see what event happennig
        # REG0x03[3:0]
        logger.debug('AS3935 interrupt callback')
        self.led.on('GREEN')
        res = self.get_INT()

        if res == 0x08:
            # INT_L: Lightning interrupt
            # todo:
            logger.debug('Lightning detected!')
            self.led.on('RED')
    
        elif res == 0x04:
            # INT_D: Disturber detected
            logger.debug('Disturber detected!')
            self.led.on('YELLOW')

        elif res == 0x01:
            # INT_NH: Noise level too high
            logger.debug('Noise level too high!')
            self.led.on('YELLOW')

        input('press any key to continue')
        sleep(1)
        self.led.all_off()

    def read(self, register):
        register = 0x40|register
        count, data = self.pi.bb_spi_xfer(AS3935.CE, [register, 0])
        # logger.debug('read register {}, res {}'.format(
        #     bytes_to_hex_str(bytes([(~0x40)&register])),
        #     bytes_to_hex_str(data)))
        if len(data) == 2:
            return data[1]
        return data

    def write(self, register, value):
        count, data = self.pi.bb_spi_xfer(AS3935.CE, [register, value])
        # logger.debug('write register {} value {}, res {}'.format(
        #     bytes_to_hex_str(bytes([register])),
        #     bytes_to_hex_str(bytes([value])),
        #     bytes_to_hex_str(data)))
        if len(data) == 2:
            return data[1]
        return data

    def tunning(self):
        # 0x08 TUN_CAP [3:0] 0000
        tun_cap_min = 0
        tun_cap_max = 0xF
        # set LCO_FDIV to 11 -> Division Ratio is 128
        res = self.read(0x03)
        self.write(0x03, 0b11000000|res)
        self.LCO_target_counts = 3906 # 500 KHz / 128 = 3.90625 KHz = 3906 Hz
        # actually 3901, delta = 5, error % = 5/3906 * 100 = .128%
        
        # output LCO in IRQ
        # logger.debug('start LCO in IRQ')
        # register = 0x08
        # res = self.read(register)
        # self.write(register, 0b10000000|res)
        # input('start tunning LCO')

        # manually found the best tun_cap
        tun_cap = 6

        # write the best tun_cap
        res = self.read(0x08)
        self.write(0x08, 0xF0&res|tun_cap)
        logger.debug('LCO tunning ok, tun_cap = {}'.format(tun_cap))
        # self.int_tunning.cancel()


    def get_distance(self):
        """
        Get the estimated distance to the head of an approaching storm. The 
        distance is updated at every single lightning event.

        Returns:
            0: default, no lightning detected
            -1: 'Out of range',
            1: 'Storm is Overhead',
            other int: KM
        """
        res = self.read(0x07)
        if res == 0b111111:
            res = -1
        return res

    def get_INT(self):
        res = self.read(0x03)
        return res&0x0F

    def set_indoor(self):
        register = 0x00
        res = self.read(register)
        self.write(register, 0b11100101&res)
        return 1

    def set_outdoor(self):
        register = 0x00
        res = self.read(register)
        self.write(0, 0b11011101&res)
        return 1
        
