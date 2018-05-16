from time import sleep
from pprint import pprint

from smbus2 import SMBusWrapper, i2c_msg

RH_ADDR = 0x40

# reset 0xfe
with SMBusWrapper(1) as bus:
    bus.write_byte(RH_ADDR, 0xfe)

# measure with master no hold mode 0xf5
# single i2c transaction with writing and reading
with SMBusWrapper(1) as bus:
    write = i2c_msg.write(RH_ADDR, [0xf5])
    bus.i2c_rdwr(write)
    sleep(1)
    
    # read 3 bytes
    read = i2c_msg.read(RH_ADDR, 3) 
    bus.i2c_rdwr(read)
    dats = list(read)
    # pprint('measure RH with no hold mode, D3 dats = {}'.format(dats))
    
# calculate humidity RH
D3 = (dats[0] << 8) + dats[1]
RH = -600 + 12500 * D3 / 2 ** 16
pprint('relative humidity = {}'.format(RH))

