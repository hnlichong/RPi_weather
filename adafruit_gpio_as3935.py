from time import sleep
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO
from utils import bytes_to_hex_str

SCLK = 40
MOSI = 38
MISO = 35
SS = 36

gpio = GPIO.get_platform_gpio(mode=RPi.GPIO.BOARD)
device = SPI.BitBang(gpio=gpio, sclk=SCLK, mosi=MOSI, miso=MISO, ss=SS)

# reset all registers to default
res = device.transfer([0x3C, 0x96])
# res (bytearray)
res = bytes_to_hex_str(res)
print('res {}'.format(res))
sleep(1)

# res = device.transfer([0x40, 0]) # b'\x00\x24'
res = device.transfer([0x41, 0]) # b'\x00\x22'
res = bytes_to_hex_str(res)
print('res {}'.format(res))

