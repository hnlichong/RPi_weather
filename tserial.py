from time import sleep
import serial

port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=3.0)

while 1:
    rcv = port.read(10)
    print('rcv {}'.format(rcv))
    sleep(1)