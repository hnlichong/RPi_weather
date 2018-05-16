from pprint import pprint
from time import sleep

from smbus2 import SMBusWrapper, i2c_msg


class MS8607(object):
    TEMP_ADDR = 0x76
    RH_ADDR = 0x40
    CAL_ADDR = (0xA2, 0xA4, 0xA6, 0xA8, 0xAA, 0xAC)
    CAL_NAME = ('C1', 'C2', 'C3', 'C4', 'C5', 'C6')
    cal_dat = {}

    def __init__(self):
        # reset device
        with SMBusWrapper(1) as bus:
            bus.write_byte(MS8607.TEMP_ADDR, 0x1e)
            bus.write_byte(MS8607.RH_ADDR, 0xfe)
        # set factory calibration data cal_dat
        self.read_factory_calibration_data()

    def read_factory_calibration_data(self):
        # read factory calibration data from PROM
        with SMBusWrapper(1) as bus:
            for name, addr in zip(MS8607.CAL_NAME, MS8607.CAL_ADDR):
                dats = bus.read_i2c_block_data(MS8607.TEMP_ADDR, addr, 2)
                MS8607.cal_dat[name] = (dats[0] << 8) + dats[1]
        return MS8607.cal_dat

    def get_temperature_pressure(self):
        C1 = MS8607.cal_dat['C1']
        C2 = MS8607.cal_dat['C2']
        C3 = MS8607.cal_dat['C3']
        C4 = MS8607.cal_dat['C4']
        C5 = MS8607.cal_dat['C5']
        C6 = MS8607.cal_dat['C6']

        with SMBusWrapper(1) as bus:
            # start conversion of temperature
            # 0x58 Convert D2 (OSR=4096) -- Temperature
            bus.write_byte(MS8607.TEMP_ADDR, 0x58)
            sleep(1)
            # read ADC
            dats = bus.read_i2c_block_data(MS8607.TEMP_ADDR, 0x00, 3)
            D2 = dats[0] * 65536 + dats[1] * 256 + dats[2]

            # start conversion of pressure            
            # 0x48 Convert D1 (OSR=4096) -- Pressure
            bus.write_byte(MS8607.TEMP_ADDR, 0x48)
            sleep(1)
            # read ADC
            dats = bus.read_i2c_block_data(MS8607.TEMP_ADDR, 0x00, 3)
            D1 = dats[0] * 65536 + dats[1] * 256 + dats[2]

        # calculate temperature
        dT = D2 - C5 * 256
        TEMP = 2000 + dT * C6 / 2 ** 23
        TEMP = round(TEMP/100, 1)
        # print('temperature = {} degrees Celsius'.format(TEMP))

        # calculate temperate compensated pressure
        OFF = C2 * 2 ** 17 + (C4 * dT) / 2 ** 6
        SENS = C1 * 2 ** 16 + (C3 * dT) / 2 ** 7
        P = (D1 * SENS / 2 ** 21 - OFF) / 2 ** 15
        P = round(P/100, 1)
        # print('pressure = {} mbar'.format(P))
        return TEMP, P

    def get_humidity(self):
        # measure with master no hold mode 0xf5
        # single i2c transaction with writing and reading
        with SMBusWrapper(1) as bus:
            write = i2c_msg.write(MS8607.RH_ADDR, [0xf5])
            bus.i2c_rdwr(write)
            sleep(1)
            
            # read 3 bytes
            read = i2c_msg.read(MS8607.RH_ADDR, 3) 
            bus.i2c_rdwr(read)
            dats = list(read)
            # pprint('measure RH with no hold mode, D3 dats = {}'.format(dats))
            
        # calculate humidity RH
        D3 = (dats[0] << 8) + dats[1]
        RH = -600 + 12500 * D3 / 2 ** 16
        RH = round(RH/100, 1)
        # pprint('relative humidity = {} %RH'.format(RH))
        return RH