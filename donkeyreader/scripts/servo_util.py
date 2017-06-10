import json
import sys
sys.path.append("app/modules")
import util
import serial
import time

conf = json.load(open("config.json"))

throttle= 0
angle = 0
direction = 1

while True:
    with serial.Serial("/dev/ttyS0", 115200, timeout=1) as ser:
        angle_pwm,throttle_pwm = util.convertToPWM(angle,throttle,conf)
        util.sendToArduino(ser,angle_pwm, throttle_pwm)    
        time.sleep(1)
        angle += direction*0.1

        if(angle>0.5 or angle<-0.5):
            direction *= -1
            angle += direction*0.1
        print("To Arduino:",angle, angle_pwm, throttle_pwm)
        while ser.inWaiting():
            ser.readline()
        line = ser.readline()   # read a '\n' terminated line
        print("From Arduino:",line)

