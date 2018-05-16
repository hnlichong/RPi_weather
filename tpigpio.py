import pigpio
from utils import bytes_to_hex_str

CE = 16
MISO = 19
MOSI = 20
SCLK = 21

pi = pigpio.pi()
if not pi.connected:
    print('pi is not connected by pigpio daemon')
    exit()


# SPI mode 1, 10 KHz
res = pi.bb_spi_open(CE, MISO, MOSI, SCLK, 10000, 1)
print('spi open res {}'.format(res))

count, data = pi.bb_spi_xfer(CE, [0x42, 0])
data = bytes_to_hex_str(data)
print('data {}'.format(data))

pi.bb_spi_close(CE)

pi.stop()