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

test_angle= True
test_throttle= False

last_send = time.time()

while True:
    with serial.Serial("/dev/ttyS0", 115200, timeout=1) as ser:
        if(time.time() - last_send > 1):
            angle_pwm,throttle_pwm = util.convertToPWM(angle,throttle,conf)
            util.sendToArduino(ser,angle_pwm, throttle_pwm)    

            if test_angle:
                angle += direction*0.1
                if(angle>0.5 or angle<-0.5):
                    direction *= -1
                    angle += direction*0.1

            if test_throttle:
                throttle += direction*0.1
                if(throttle>1.0 or throttle<0.0):
                    direction *= -1
                    throttle += direction*0.1

            print("To Arduino:",angle,throttle, angle_pwm, throttle_pwm)
            last_send = time.time()

        ser.readline()
        line = ser.readline()   # read a '\n' terminated line
        #decoded = util.decode_line(line,conf)
        #print("From Arduino: %s decoded: %s" % (line.decode(), ",".join([str(f) for f in decoded])))
        

