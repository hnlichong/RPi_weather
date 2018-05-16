
import pigpio
from time import sleep


pi = pigpio.pi()

IRQ = 26
def cbf(gpio, level, tick):
    print(gpio, level, tick)

# set IRQ pull down, as IRQ goes high for interrupt
pi.set_pull_up_down(IRQ, pigpio.PUD_DOWN)
cb1 = pi.callback(IRQ, pigpio.RISING_EDGE, cbf)

sleep(10)

cb1.cancel() # To cancel callback cb1.

pi.stop()


