import wiringpi

BUTTON1 = 4

# init wiringpi
wiringpi.wiringPiSetup()

# interrupt
# int wiringPiISR (int pin, int edgeType,  void (*function)(void));
def gpio_callback():
    print("GPIO_CALLBACK!")

wiringpi.pinMode(BUTTON1, wiringpi.GPIO.INPUT)
wiringpi.pullUpDnControl(BUTTON1, wiringpi.GPIO.PUD_UP)

wiringpi.wiringPiISR(BUTTON1, wiringpi.GPIO.INT_EDGE_BOTH, gpio_callback)

while True:
    wiringpi.delay(2000)