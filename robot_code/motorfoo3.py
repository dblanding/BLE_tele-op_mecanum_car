import time
from machine import Pin, PWM
from pico_car import Motor

motor = Motor()
speed = 0
# motor.motor_stop()
m1 = motor.motor_left_front
m2 = motor.motor_right_front
m3 = motor.motor_right_back
m4 = motor.motor_left_back
motors = [m1, m2, m3, m4]
speeds = [0, 20, 40, 60, 80, 60, 40, 20, 0, -20, -40, -60, -80, -60, -40, -20, 0]
try:
    for mtr in motors:
        for spd in speeds:
            if spd < 0:
                direction = -1
            else:
                direction = 1
            mtr(1, direction, abs(spd))
            time.sleep(0.25)
finally:
    motor.motor_stop()
