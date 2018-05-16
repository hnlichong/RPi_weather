from time import sleep
from pprint import pprint
import smbus
DEVICE_BUS = 1
TEMP_ADDR = 0x76
RH_ADDR = 0x40
CAL_ADDR = (0xA2, 0xA4, 0xA6, 0xA8, 0xAA, 0xAC)
CAL_NAME = ('C1', 'C2', 'C3', 'C4', 'C5', 'C6')
bus = smbus.SMBus(DEVICE_BUS)


# reset
bus.write_byte(TEMP_ADDR, 0x1e)

# read factory calibration data from PROM
# 0xAA  C5 -- Reference temperature
# 0xAC  C6 -- Temperature coefficient of the temperature 
cal_data = {}
for name, addr in zip(CAL_NAME, CAL_ADDR):
    dats = bus.read_i2c_block_data(TEMP_ADDR, addr)
    cal_data[name] = dats[0] * 256 + dats[1]
# pprint('cal_data = {}'.format(cal_data))
C1 = cal_data['C1']
C2 = cal_data['C2']
C3 = cal_data['C3']
C4 = cal_data['C4']
C5 = cal_data['C5']
C6 = cal_data['C6']

# start conversion 
# 0x58 Convert D2 (OSR=4096) -- Temperature
# 0x48 Convert D1 (OSR=4096) -- Pressure
bus.write_byte(TEMP_ADDR, 0x58)
sleep(1)
# read ADC
dats = bus.read_i2c_block_data(TEMP_ADDR, 0x00)
D2 = dats[0] * 65536 + dats[1] * 256 + dats[2]

bus.write_byte(TEMP_ADDR, 0x48)
sleep(1)
# read ADC
dats = bus.read_i2c_block_data(TEMP_ADDR, 0x00)
D1 = dats[0] * 65536 + dats[1] * 256 + dats[2]


# calculate temperature
dT = D2 - C5 * 256
TEMP = 2000 + dT * C6 / 2 ** 23
print('temperature = {}'.format(TEMP))

# calculate temperate compensated pressure
OFF = C2 * 2 ** 17 + (C4 * dT) / 2 ** 6
SENS = C1 * 2 ** 16 + (C3 * dT) / 2 ** 7
P = (D1 * SENS / 2 ** 21 - OFF) / 2 ** 15
print('pressure = {}'.format(P))
