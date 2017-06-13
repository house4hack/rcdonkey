import glob
import serial
import picamera
import time
import modules.camera as cam
import cv2
import struct
import traceback
import json
import modules.util as util
import os.path

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


def make_recording_folder(parent_folder):
    l = glob.glob("%s/record_*" % parent_folder)
    l.sort()
    if len(l)>0:
        last_record = l[-1]
        parts = last_record.split("_")
        number = int(parts[1])+1
    else:
        number = 1
    return("%s/record_%05d/" % (parent_folder, number))

is_recording= False
is_deciding=False
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
                if not is_recording:
                    util.mount()
                    recording_folder = make_recording_folder(conf["save_folder"])
                    if not os.path.exists(recording_folder):
                        os.makedirs(recording_folder)
                    is_recording = True
                frame = camera.grabFrame()
                filename = create_img_filepath(recording_folder,frame_no,angle, throttle, 0.0)
                print(filename)
                cv2.imwrite(filename, frame)
                frame_no+=1
            else:
                if is_recording:
                    is_recording = False                    
                    util.umount()

            if dodecide:
                if not is_deciding:
                    util.mount()
                    is_deciding = True
                frame = camera.grabFrame()
                angle,throttle = pilot.decide(frame)
                angle_pwm,throttle_pwm= util.convertToPWM(angle, throttle,conf) 
                print("To Arduino: %.2f: angle=%.2f throttle=%.2f angle_pwm=%d throttle_pwm=%d" % (time.time(), angle,throttle, angle_pwm, throttle_pwm))
                util.sendToArduino(ser,angle_pwm,throttle_pwm)
            else:
                if is_deciding:
                    util.umount()
                    is_deciding = False
                time.sleep(0.1)
        except Exception as e:
            print(e)
            traceback.print_exc()
