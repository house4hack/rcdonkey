import glob
import serial
import picamera
import time
import modules.camera as cam
import cv2
#import donkey


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



i=0
while True:
    with serial.Serial(port, 115200, timeout=1) as ser:
        while ser.in_waiting:  # Or: while ser.inWaiting():
            ser.readline()
        line = ser.readline()   # read a '\n' terminated line
        try:
            parts = line.strip().split(",")
            throttle = (float(parts[0])-1000.0)/1000.0
            if throttle<0:
                throttle = 0.0
            angle = (float(parts[1]) - 1000.0)/1000.0-0.5
            dorecord = float(parts[2])>1500
            print(throttle,angle,i, dorecord)
            if dorecord:
                #camera.capture("frame_%05d_ttl_%.2f_agl_%.2f_mil_0.0.jpg" % (i,throttle,angle), resize = (160,120),  use_video_port=True)         
                frame = camera.grabFrame()
                filename = create_img_filepath("/home/pi/record",i,angle, throttle, 0.0)
                cv2.imwrite(filename, frame)
                i+=1
            else:
                time.sleep(0.1)
        except Exception as e:
            print(e)
