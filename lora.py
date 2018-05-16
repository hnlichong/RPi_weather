from time import sleep
import wiringpi
import utils

CHANNEL = 0
SPI0_CE0 = 10
RESET = 7

# init wiringPi
wiringpi.wiringPiSetup()

# CHANNEL 1, 1 MHz
# int wiringPiSPISetup (int CHANNEL, int speed) 
# return linux file-description
fd = wiringpi.wiringPiSPISetup(CHANNEL, 1000000)
print('fd {}, SPI frequency: {}'.format(fd, 1000000))

# reset device  
wiringpi.pinMode(RESET, wiringpi.OUTPUT)
wiringpi.digitalWrite(RESET, wiringpi.LOW)
sleep(1)
wiringpi.digitalWrite(RESET, wiringpi.HIGH)

# CS: low active 
wiringpi.pinMode(SPI0_CE0, wiringpi.OUTPUT)
wiringpi.digitalWrite(SPI0_CE0, wiringpi.LOW)

# wiringpi.wiringPiSPIDataRW (int CHANNEL, unsigned char *data, int len)

# read the register
buf = bytes([0x42, 0]) # revision, ret 0x12
# buf = bytes([0x44, 0]) # ret 0x2d
# buf = bytes([0x01, 0]) # opmode
retlen, retdata = wiringpi.wiringPiSPIDataRW(CHANNEL, buf)
retdata = utils.bytes_to_hex_str(retdata)
print('retlen {}, retdata {}, buf {}'.format(retlen, retdata, buf))
