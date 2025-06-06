import time
from machine import Pin, PWM

speed = 0

# left front wheel M1
Motor_LF_PWM = PWM(Pin(12))
Motor_LF_Dir = Pin(13, Pin.OUT)
# right front wheel M2
Motor_RF_PWM = PWM(Pin(15))
Motor_RF_Dir = Pin(14, Pin.OUT)
# right back wheel M3
Motor_RB_PWM = PWM(Pin(16))
Motor_RB_Dir = Pin(17, Pin.OUT)
# left back wheel M4
Motor_LB_PWM = PWM(Pin(19))
Motor_LB_Dir = Pin(18, Pin.OUT)

# mapping function
def map(x, in_max, in_min, out_max, out_min):
    return (x - in_min)/(in_max - in_min)*(out_max - out_min) + out_min

def all_stop():
    Motor_LF_Dir.low()
    Motor_LF_PWM.duty_u16(0)
    Motor_LB_Dir.low()
    Motor_LB_PWM.duty_u16(0)
    Motor_RF_Dir.low()
    Motor_RF_PWM.duty_u16(0)
    Motor_RB_Dir.low()
    Motor_RB_PWM.duty_u16(0)
        

'''
Motor interface.
    M1  _____  M2
       |     |
       |     |
       |     |
    M4 |_____| M3

'''

def mtr1(dir, spd):
    """
    Run motor
    Args: dir = 1 (CW) or -1 (CCW)
          spd = integer from 0 to 100 (> 40 to overcome friction)
    """
    value = int(map(spd, 100, 0, 65535, 0))
    Motor_LF_PWM.freq(500)
    if dir == -1:  # CCW
        Motor_LF_Dir.low()
        Motor_LF_PWM.duty_u16(int(value))
    elif dir == 1:  # CW
        Motor_LF_Dir.high()
        Motor_LF_PWM.duty_u16(value)

def mtr2(dir, spd):
    """
    Run motor
    Args: dir = 1 (CW) or -1 (CCW)
          spd = integer from 0 to 100 (> 40 to overcome friction)
    """
    value = int(map(spd, 100, 0, 65535, 0))
    Motor_RF_PWM.freq(500)
    if dir == 1:  # CW
        Motor_RF_Dir.low()
        Motor_RF_PWM.duty_u16(int(value))
    elif dir == -1:  # CCW
        Motor_RF_Dir.high()
        Motor_RF_PWM.duty_u16(value)

def mtr3(dir, spd):
    """
    Run motor
    Args: dir = 1 (CW) or -1 (CCW)
          spd = integer from 0 to 100 (> 40 to overcome friction)
    """
    value = int(map(spd, 100, 0, 65535, 0))
    Motor_RB_PWM.freq(500)
    if dir == -1:  # CCW
        Motor_RB_Dir.low()
        Motor_RB_PWM.duty_u16(int(value))
    elif dir == 1:  # CW
        Motor_RB_Dir.high()
        Motor_RB_PWM.duty_u16(value)

def mtr4(dir, spd):
    """
    Run motor
    Args: dir = 1 (CW) or -1 (CCW)
          spd = integer from 0 to 100 (> 40 to overcome friction)
    """
    value = int(map(spd, 100, 0, 65535, 0))
    Motor_LB_PWM.freq(500)
    if dir == 1:  # CW
        Motor_LB_Dir.low()
        Motor_LB_PWM.duty_u16(int(value))
    elif dir == -1:  # CCW
        Motor_LB_Dir.high()
        Motor_LB_PWM.duty_u16(value)


for mtr in (mtr1, mtr2, mtr3, mtr4):
    mtr(1, speed)
    time.sleep(1)
    all_stop()
    mtr(-1, speed)
    time.sleep(1)
    all_stop()
