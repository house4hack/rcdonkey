import glob
import serial
import picamera
import time
import modules.camera as cam
import cv2
import struct
import traceback
import json
import util

conf = json.load(open("config.json"))

if conf['load_pilot']:
    import donkey
    from donkey.pilots import KerasCategorical
    pilot = KerasCategorical(conf["model"])
    pilot.load()


camera = cam.Camera(True,width=160,height=120)

l = glob.glob("/dev/ttyS0")
port = l[0]

def create_img_filepath(directory, frame_count, angle, throttle, milliseconds):
    filepath = str("%s/" % directory +
                "frame_" + str(frame_count).zfill(5) +
                "_ttl_" + str(throttle) +
                "_agl_" + str(angle) +
                "_mil_" + str(milliseconds) +
                '.jpg')
    return filepath





frame_no=0
while True:
    with serial.Serial(port, 115200, timeout=1) as ser:
        while ser.inWaiting():
            ser.readline()
        line = ser.readline()   # read a '\n' terminated line
        try:
            line = line.decode('utf-8')
            parts = line.strip().split(",")
            angle,throttle = util.convertFromPWM(parts[1],parts[0],conf)
            dorecord = parts[3]=="1"
            dodecide = parts[2]!="0"
            print("From Arduino:",throttle,angle,frame_no, dorecord,dodecide)

            if dorecord:
                frame = camera.grabFrame()
                filename = create_img_filepath(conf["save_folder"],frame_no,angle, throttle, 0.0)
                cv2.imwrite(filename, frame)
                frame_no+=1
            if dodecide:
                frame = camera.grabFrame()
                angle,throttle = pilot.decide(frame)
                #angle = max(-1, min(1,angle))
                #throttle = max(0, min(1,throttle))

                angle_pwm,throttle_pwm= util.convertToPWM(angle, throttle,conf) 
                print("To Arduino: %.2f: angle=%.2f throttle=%.2f angle_pwm=%d throttle_pwm=%d" % (time.time(), angle,throttle, angle_pwm, throttle_pwm))
                util.sendToArduino(ser,angle_pwm,throttle_pwm)
            else:
                time.sleep(0.1)
        except Exception as e:
            print(e)
            traceback.print_exc()
