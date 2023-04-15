import time
import sys
from Adafruit_BME280 import *
import RPi.GPIO as GPIO
from gpiozero import MCP3008
from gpiozero import PWMLED
import time

# pin set up
ledRedPin = 40
# set up by numbering
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ledRedPin, GPIO.OUT)
# ADC set up
photocell = MCP3008(7)  # channel 7

print('Fog node running... Press CTRL+C to exit')

try:
    # init BME280
    sensor = BME280(t_mode=BME280_OSAMPLE_8,
                    p_mode=BME280_OSAMPLE_8,
                    h_mode=BME280_OSAMPLE_8)

    while True:
        degrees = sensor.read_temperature()
        light = photocell.value

        print('Temp      = {0:0.3f} deg C'.format(degrees))
        print('Analogue Value = {}; Voltage = {}v'.format(light, light * 3.3))

        # GPIO.output(ledRedPin, True)
        if (degrees > 20 and light > 0.8):
            GPIO.output(ledRedPin, False)
        else:
            GPIO.output(ledRedPin, True)

        time.sleep(1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print('Fog node terminated!')
