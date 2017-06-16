import struct
import subprocess
import os.path
import glob
import time
from donkey.pilots import KerasCategorical


def convertToPWM(angle,throttle,conf):
    angle = max(-1.0, angle)
    angle = min(1.0, angle)

    throttle = max(0, throttle)
    throttle = min(1, throttle)

    angle_pwm    = (angle)*(conf['max_angle_pwm'] - conf['min_angle_pwm']) +  conf['mid_angle_pwm']
    throttle_pwm = throttle * (conf['max_throttle_pwm'] - conf['min_throttle_pwm'])  + conf['min_throttle_pwm']

    return(angle_pwm, throttle_pwm)

def convertFromPWM(angle_pwm, throttle_pwm, conf):
    throttle = (float(throttle_pwm)-conf['min_throttle_pwm'])/float(conf['max_throttle_pwm'] - conf['min_throttle_pwm'])
    angle = (float(angle_pwm) - conf['mid_angle_pwm'] )/float(conf['max_angle_pwm'] - conf['min_angle_pwm'])  
    return(angle,throttle)

def sendToArduino(ser,angle,throttle):
    dataToSend = struct.pack('<BBhh', ord('A'), ord('A'),int(angle),int(throttle))
    #ser.write('AA'.encode())
    ser.write(dataToSend)


def ismounted():
    '''checks if USB_AI_RC_Car_Stick is mounted'''
    vpath = "/home/pi/record"
    return(os.path.ismount(vpath))


def mount():
    '''mounts USB_AI_RC_Car_Stick'''
    vpath = "/home/pi/record"
    if not ismounted():
        cmd = 'sudo mount /dev/sda1 ' + vpath
        proc = subprocess.Popen(str(cmd), shell=True, stdout=subprocess.PIPE).stdout.read()
        print(proc)
    else:
        print("Was already mounted, skipping")

def umount():
    '''unmounts USB_AI_RC_Car_Stick'''
    vpath = "/home/pi/record"
    if ismounted():
        cmd = 'sudo umount ' + vpath
        proc = subprocess.Popen(str(cmd), shell=True, stdout=subprocess.PIPE).stdout.read()
        print(proc)
    else:
        print("Not mounted, skipping")

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
    recording_folder = "%s/record_%05d/" % (parent_folder, number)
    if not os.path.exists(recording_folder):
        os.makedirs(recording_folder)
    return(recording_folder)

def decode_line(line,conf):
    line = line.decode('utf-8')
    parts = line.strip().split(",")
    angle,throttle = convertFromPWM(parts[1],parts[0],conf)
    dorecord = parts[3]=="1"
    dodecide = parts[2]!="0"
    return(angle,throttle,dorecord,dodecide)

def check_and_load_pilot(model_folder, last_model_name, last_model_time, pilot=None):
    '''check if model has changed on disk and load pilot'''
    l = glob.glob("%s/*.hdf5" % model_folder)
    if len(l)==0:
        print("Could not find model file!")
        umount()
    elif len(l)>0:
        model_file = l[0]
        model_time = time.strftime('%m/%d/%Y', time.gmtime(os.path.getmtime(model_file)))
        if not last_model_name==model_file and not last_model_time == model_time:
            pilot = KerasCategorical(model_file)
            pilot.load()            
        last_model_name = model_file
        last_model_time = model_time
    return(last_model_name, last_model_time, pilot)

