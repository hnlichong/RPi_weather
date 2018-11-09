import pigpio
from led import led

if __name__ == '__main__':
    led.all_off()
    pigpio.pi().stop()
