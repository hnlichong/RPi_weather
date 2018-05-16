"""
test lora with spi bit-bang
"""
from time import sleep
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO
from utils import bytes_to_hex_str

SCLK = 23
MOSI = 19
MISO = 21
SS = 24

gpio = GPIO.get_platform_gpio(mode=RPi.GPIO.BOARD)
device = SPI.BitBang(gpio=gpio, sclk=SCLK, mosi=MOSI, miso=MISO, ss=SS)

# reset all registers to default

# revision, ret 0x12
res = device.transfer([0x42, 0])
res = bytes_to_hex_str(res)
print('res {}'.format(res))

# test, ret 0x2d
res = device.transfer([0x44, 0])
res = bytes_to_hex_str(res)
print('res {}'.format(res))



