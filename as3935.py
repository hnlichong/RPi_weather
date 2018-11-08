from time import sleep, time
import pigpio
from utils import bytes_to_hex_str
from utils import my_logger
import os

logger = my_logger(__name__, level="DEBUG")
root_path = os.path.dirname(os.path.abspath(__file__))

class AS3935(object):
    CE = 16
    MISO = 19
    MOSI = 20
    SCLK = 21
    IRQ = 12

    def __init__(self, pi):
        self.pi = pi

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

        # choose occasion
        self.set_outdoor() # 室外模式下 前置放大器的放大倍数低一些
        # self.set_indoor()

        # Antenna Tuning
        self.tunning()

        # 折衷：闪电检测效率 vs 噪声干扰抑制能力
        self.write(0x01, 0b00100001)
        self.write(0x02, 0b11000010)

        # init lightning interrupt
        self.int = self.pi.callback(
            AS3935.IRQ, pigpio.RISING_EDGE, self._cb_int)
        sleep(0.5)
        # 重置中断标志位
        # 读取一次中断寄存器就会自动重置中断标志位
        self.INT_res = self.read_INT()

        self.lightning_cbs = []

    def __del__(self):
        self.pi.bb_spi_close(AS3935.CE)        

    def _cb_int(self, gpio, level, tick):
        # read interrupt resigter to see what event happennig
        # REG0x03[3:0]
        logger.debug('AS3935 interrupt callback')
        res = self.read_INT()
        self.INT_res = res

        if res == 0x08:
            # INT_L: Lightning interrupt
            logger.debug('Lightning detected!')
            for cb in self.lightning_cbs:
                if callable(cb):
                    cb()

        elif res == 0x04:
            # INT_D: Disturber detected
            logger.debug('Disturber detected!')

        elif res == 0x01:
            # INT_NH: Noise level too high
            logger.debug('Noise level too high!')

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
        # 根据示波器实测得到，写死配置值
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

    def read_INT(self):
        """读取中断寄存器
        注意:读取一次中断寄存器就会自动重置中断标志位
        Returns:
            0x08 INT_L: Lightning interrupt
            0x04 INT_D: Disturber detected
            0x01 INT_NH: Noise level too high
        """
        res = self.read(0x03)
        return res & 0x0F

    def get_INT_res(self):
        """读取中断寄存器，读完后清零"""
        res = self.INT_res
        self.INT_res = 0x00
        return res

    def set_indoor(self):
        register = 0x00
        res = self.read(register)
        self.write(register, 0b11100101&res)
        logger.debug('indoor mode')
        return 1

    def set_outdoor(self):
        register = 0x00
        res = self.read(register)
        self.write(0, 0b11011101&res)
        logger.debug('outdoor mode')
        return 1


# 单例模式
pi = pigpio.pi()
if not pi.connected:
    print('pi is not connected by pigpio daemon')
    exit()
as3935 = AS3935(pi)