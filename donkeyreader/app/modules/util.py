import struct

def convertToPWM(angle,throttle,conf):
    angle_pwm    = (angle+0.5)*1000 + 1000
    throttle_pwm = throttle * 1000  + 1000

    angle_pwm = max(conf['min_angle_pwm'], angle_pwm)
    angle_pwm = min(conf['max_angle_pwm'], angle_pwm)

    throttle_pwm = max(conf['min_throttle_pwm'], throttle_pwm)
    throttle_pwm = min(conf['max_throttle_pwm'], throttle_pwm)
    return(angle_pwm, throttle_pwm)

def convertFromPWM(angle_pwm, throttle_pwm, conf):
    throttle = (float(throttle_pwm)-1000.0)/1000.0
    angle = (float(angle_pwm) - 1000.0)/1000.0-0.5
    return(angle,throttle)

def sendToArduino(ser,angle,throttle):
    dataToSend = struct.pack('<hh', int(angle),int(throttle))
    ser.write('AA'.encode())
    ser.write(dataToSend)
