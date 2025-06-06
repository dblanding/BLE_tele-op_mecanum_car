import time
from machine import Pin, PWM
from pico_car import Motor

motor = Motor()
speed = 0
stop = motor.motor_stop

M1 = motor.motor_left_front
M2 = motor.motor_right_front
M3 = motor.motor_right_back
M4 = motor.motor_left_back

'''
Motor interface.
    M1  _____  M2
       |     |
       |     |
       |     |
    M4 |_____| M3


(1, 1, 100) ---(status, direction, speed)
 |  |   |
 |  |   speed: value range 0~100.
 |  direction: 1(forward), -1(backward)
status: 1(move), 0(stop)

M1 -> motor.motor_left_front(status, direction, speed)
M2 -> motor.motor_right_front(status, direction, speed)
M3 -> motor.motor_right_back(status, direction, speed)
M4 -> motor.motor_left_back(status, direction, speed)
'''
directions = [
    "forward",
    "backward",
    "right",
    "left",
    "right_forward",
    "left_forward",
    "right_backward",
    "left_backward",
    "turn_left",
    "turn_right",
    ]
    
try:
    '''
    for M in (M1, M2, M3, M4):
        M(1, 1, speed)
        time.sleep(2)
        stop()
        M(1, -1, speed)
        stop()
        time.sleep(2)
    '''
    for direction in directions:
        motor.move(1, direction, speed)
        time.sleep(1)
finally:
    motor.motor_stop()
