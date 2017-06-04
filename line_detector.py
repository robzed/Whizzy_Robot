'''
Created on 3 Jun 2017

@author: rob
'''

# See https://picamera.readthedocs.io/en/release-1.13/recipes1.html

import time
from whizzy_indications import working
try:
    from picamera import PiCamera
except ImportError:
    from test_stubs.picamera_stub import PiCamera_stub as PiCamera

import whizzy_indications as indications

class LineDetector():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.started = False
        
    def start(self):
        self.image_width = 320  # width should be /32
        self.image_height = 240 # height should be /16

        camera = PiCamera()
        #camera.resolution = (1024, 768)
        camera.exposure_mode = 'sports'
        camera.start_preview()
        # Need to allow camera warm-up time
        self.camera = camera
        # image data is YUV420, which is chroma data is /2 in both horizontal and vertical
        # i.e. 1 byte of u and 1 byte of v for every 4 (2x2 square) bytes
        # therefore size of array is w * h * 1.5 
        self.buf = bytearray(int(self.image_height*self.image_width*1.5))
        self.started = True
        
    def stop(self):
        self.camera.close()
        self.started = False
        
    def capture(self):
        start = time.perf_counter()
        #output = np.empty((240, 320, 3), dtype=np.uint8)
        self.camera.capture(self.buf, 'yuv', resize=(self.image_width, self.image_height))
        print("Time = %.1f ms" % (1000 * (time.perf_counter() - start)))
    
    def calibrate(self):
        if not self.started:
            self.start()
        
        indications.working(2)
        self.capture()
        print(self.buf)
