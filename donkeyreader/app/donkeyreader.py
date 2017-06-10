import glob
import serial
import picamera
import time
import modules.camera as cam
import cv2
import struct
import traceback

pilot_loaded = False




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

def sendToArduino(ser,angle,throttle):
  dataToSend = struct.pack('<hh', int(angle),int(throttle))
  ser.write('AA'.encode())
  ser.write(dataToSend)


def convertToPWM(angle,throttle):
    angle_pwm    = (angle+0.5)*1000 + 1000
    throttle_pwm = throttle * 1000  + 1000
    return(angle_pwm, throttle_pwm)

def convertFromPWM(angle_pwm, throttle_pwm):
    throttle = (float(throttle_pwm)-1000.0)/1000.0
    angle = (float(angle_pwm) - 1000.0)/1000.0-0.5
    return(angle,throttle)


frame_no=0
while True:
    with serial.Serial(port, 115200, timeout=1) as ser:
        while ser.inWaiting():
            ser.readline()
        line = ser.readline()   # read a '\n' terminated line
        try:
            line = line.decode('utf-8')
            parts = line.strip().split(",")
            #throttle = (float(parts[0])-1000.0)/1000.0
            #angle = (float(parts[1]) - 1000.0)/1000.0-0.5
            angle,throttle = convertFromPWM(parts[1],parts[0])
            dorecord = parts[3]=="1"
            dodecide = parts[2]!="0"
            print("From Arduino:",throttle,angle,frame_no, dorecord,dodecide)
            if dorecord:
                frame = camera.grabFrame()
                filename = create_img_filepath("/home/pi/record",frame_no,angle, throttle, 0.0)
                cv2.imwrite(filename, frame)
                frame_no+=1
            if dodecide:
                if not pilot_loaded:
                    import donkey
                    from donkey.pilots import KerasCategorical
                    pilot = KerasCategorical("/home/pi/mydonkey/models/default.h5")
                    pilot.load()
                    pilot_loaded= True
                frame = camera.grabFrame()
                angle,throttle = pilot.decide(frame)
                angle = max(-1, min(1,angle))
                throttle = max(0, min(1,throttle))

                print("To Arduino: %.2f: angle=%.2f throttle=%.2f" % (time.time(), angle,throttle))
                angle_pwm,throttle_pwm= convertToPWM(angle, throttle) 
                sendToArduino(ser,angle_pwm,throttle_pwm)
            else:
                time.sleep(0.1)
        except Exception as e:
            print(e)
            traceback.print_exc()
