from machine import Pin, ADC
from math import pi
import time
from geom2d import r2p, p2r

adc_x = ADC(Pin(26))
adc_y = ADC(Pin(27))
adc_z = ADC(Pin(28))

def read_joystk():
    js_x = round(adc_x.read_u16() * (20 / 65535.0) - 10)
    js_y = round(adc_y.read_u16() * (20 / 65535.0) - 10)
    js_z = round(adc_z.read_u16() * (20 / 65535.0) - 10)
    return js_x, js_y, js_z

def read_joystk():
    """Rotated 45 degrees"""
    # get joystick axis values
    js_x = adc_x.read_u16()
    js_y = adc_y.read_u16()
    js_z = adc_z.read_u16()
    
    # convert u16 values to values between -10 and +10
    x = js_x * (20 / 65535.0) - 10
    y = js_y * (20 / 65535.0) - 10
    z = js_z * (20 / 65535.0) - 10

    # rotate joystick by 45 degrees
    r, theta = r2p(x, y)
    theta -= pi/4
    x, y = p2r(r, theta)
    
    return round(x), round(y), round(z)
    
while True:
    x, y, z = read_joystk()
    print(f"{x}\t{y}\t{z}")
    time.sleep(0.5)
    
