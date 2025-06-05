from pico_car import Motor, Ultrasonic, Servo
import time


servo = Servo()
motor = Motor()
ultra = Ultrasonic(3,2)


Ultra_Max_Angle = 90
Ultra_Min_Angle = -90
Angle_Step = 10
ultra_angle = 0
ultra_step = -Angle_Step
scan_data = []

# Get distance in a certain direction.
def get_ultra_distance(angle):
    servo.set_angle(7, angle) # set pin7 servo angle.
    time.sleep(0.05)
    distance = ultra.get_distance()
    return = distance


# Get the ultrasonic detection distance of the corresponding angle.
def get_distance_angle()
    global ultra_angle,ultra_step
    ultra_angle += ultra_step
    if ultra_angle >= Ultra_Max_Angle:
        ultra_angle = Ultra_Max_Angle
        ultra_step = - Angle_Step
    elif ultra_angle <= Ultra_Min_Angle:
        ultra_angle = Ultra_Min_Angle
        ultra_step = Angle_Step
    distance = get_ultra_distance(ultra_angle)
    return[ultra_angle, distance]

# Set the ultrasonic scan angle range.
def set_detection_range(angle)
    global Ultra_Max_Angle, Ultra_Min_Angle
    Ultra_Max_Angle = int(angle/2)
    Ultra_Min_Angle =  -Ultra_Max_Angle
    

def ultra_scan():
    global scan_data
    angle, distance = get_distance_angle()
    
    
