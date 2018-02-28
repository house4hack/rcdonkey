import io
import os
import time
from threading import Thread
from itertools import cycle

import numpy as np

from PIL import Image
import modules.util as util


class PiVideoStream():
    def __init__(self, resolution=(160, 120), framerate=20):
        from picamera.array import PiRGBArray
        from picamera import PiCamera

        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="rgb", use_video_port=True)
 
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False
        
        print('PiVideoStream loaded.. .warming camera')

        time.sleep(2)
        self.start()

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        time.sleep(1)
        return self

 
    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)
 
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return


    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def read(self):
        return self.frame

    def capture_arr(self):
        return self.read()

    def capture_img(self):
        arr = self.capture_arr()
        print(type(arr))
        img = Image.fromarray(arr, 'RGB')
        return img
        
    def capture_binary(self):
        img = self.capture_img()
        return util.img_to_binary(img)
