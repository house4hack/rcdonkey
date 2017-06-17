import glob
import serial

import time
import struct
import traceback
import json
import modules.util as util
import os.path

import donkey
import donkey.utils
import donkey.sensors

conf = json.load(open("config.json"))

import picamera
camera = donkey.sensors.PiVideoStream()
camera.start()

l = glob.glob("/dev/ttyS0")
port = l[0]

is_recording= False
is_deciding=False
last_model_name=""
last_model_time=""
pilot = None
frame_no=0
while True:
    with serial.Serial(port, 115200, timeout=1) as ser:
        while ser.inWaiting():
            ser.readline()
        line = ser.readline()   # read a '\n' terminated line
        try:
            angle,throttle,dorecord,dodecide = util.decode_line(line,conf)
            print("From Arduino:",throttle,angle,frame_no, dorecord,dodecide)

            # Do we record? 
            if dorecord:
                # mount and create new folder to store images
                if not is_recording:
                    util.mount()
                    recording_folder = util.make_recording_folder(conf["save_folder"])
                    is_recording = True

                # get image from camera and save to disk
                frame = camera.capture_arr()
                filename = util.create_img_filepath(recording_folder,frame_no,angle, throttle, 0.0)
                print(filename)
                img = donkey.utils.arr_to_img(frame)
                img.save(filename)
                frame_no+=1
            else:
                # unmount when we are done
                if is_recording:
                    is_recording = False                    
                    util.umount()

            # are we deciding?
            if dodecide:
                # load the pilot only if it has changed based on name and change date
                if not is_deciding:
                    util.mount()
                    last_model_name, last_model_time, pilot = util.check_and_load_pilot(conf["model_folder"], last_model_name, last_model_time, pilot)
                    if pilot != None:
                        is_deciding = True
                    if not is_recording:
                        util.umount()

                if is_deciding:
                    frame = camera.capture_arr()
                    angle,throttle = pilot.decide(frame)
                    angle_pwm,throttle_pwm= util.convertToPWM(angle, throttle,conf) 
                    print("To Arduino: %.2f: angle=%.2f throttle=%.2f angle_pwm=%d throttle_pwm=%d" % (time.time(), angle,throttle, angle_pwm, throttle_pwm))
                    util.sendToArduino(ser,angle_pwm,throttle_pwm)
            else:
                # finished deciding
                if is_deciding:
                    is_deciding = False

                time.sleep(0.1)
        except Exception as e:
            print(e)
            traceback.print_exc()
