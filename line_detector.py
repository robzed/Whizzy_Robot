'''
Created on 3 Jun 2017

@author: rob
'''

# See https://picamera.readthedocs.io/en/release-1.13/recipes1.html
# Consider numpy for these operations


try:
    from picamera import PiCamera
except ImportError:
    from test_stubs.picamera_stub import PiCamera_stub as PiCamera

from test_stubs.image_services import save_image

import whizzy_indications as indications

class LostLineException(Exception):
    pass

class LineDetector():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.started = False
        self.failed_flag = False
        
        #test_img = bytearray(self.image_height*self.image_width)
        #for x in range(self.image_width // 2):
        #    for y in range(self.image_height // 3):
        #        test_img[x + ((y * self.image_width))] = 200
        #
        #self.save_image("test.bmp", test_img)

    def failed(self):
        return self.failed_flag

    def save_image(self, filename, img_data, bpp=8):
        save_image(filename, img_data, bpp, self.image_width, self.image_height)
    

        
    def start(self):
        self.image_width = 320  # width should be /32
        self.image_height = 240 # height should be /16
        self.h_center = self.image_width // 2        # adjust this to adjust center of image
        self.line_to_process = 90 # self.image_height // 2
    
        camera = PiCamera()
        #camera.resolution = (1024, 768)
        camera.exposure_mode = 'sports'
        camera.start_preview(alpha=128)
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
        #start = time.perf_counter()
        #output = np.empty((240, 320, 3), dtype=np.uint8)
        self.camera.capture(self.buf, 'yuv', resize=(self.image_width, self.image_height))
        #print("Time = %.1f ms" % (1000 * (time.perf_counter() - start)))
        #self.save_image("yuv_convert.bmp", self.buf)
    def calibrate(self):
        if not self.started:
            self.start()
        
        indications.working(2)
        self.capture()
        self.calibrate_scan_line(self.line_to_process)

    def create_test_image(self, mid_point):
        test_image = bytearray(self.image_height * self.image_width)
        for i in range(self.image_height * self.image_width):
            if self.buf[i] > mid_point:
                test_image[i] = 0
            else:
                test_image[i] = 255
        self.save_image("level_based_output.bmp", test_image)

        
    def calibrate_scan_line(self, line):
        line_start = line * self.image_height
        line_data = self.buf[line_start : (line_start+self.image_width)]

        low = min(line_data)
        high = max(line_data)
        if high-low < 10:
            print("Not enough contrast to calibrate")
            indications.warning(2)
            self.failed_flag = True
            return
        
        mid = ((high - low) // 2) + low
        
        #for i in line_data:
        #    print(i, end=',')
        #self.create_test_image(mid)
        
        stage = 0
        for i in line_data:
            if stage == 0:
                if i > mid:
                    stage = 1
            elif stage == 1:
                if i <= mid:
                    stage = 2
            else:
                if i >= mid:
                    stage = 3
                    break

        if stage != 2:
            print("No clear line detected based on mid-point")
            indications.warning(2)
            self.failed_flag = True
            return

        in_ = bytearray(256)
        out = bytearray(256)
        for i in range(0, mid):
            in_[i] = i
            out[i] = 0
        for i in range(mid, 256):
            in_[i] = i
            out[i] = 0
        self.t = bytearray.maketrans(in_, out)
        
        x = line_data.translate(self.t)
        start = x.find(1)
        if start == -1:
            print("Couldn't find start of line")
            indications.warning(2)
            self.failed_flag = True
            return
        
        end = x.find(0, start)
        if end == -1:
            print("Couldn't find end of line")
            indications.warning(2)
            self.failed_flag = True
            return
        
        if end-start < 3:
            print("Line too narrow to be taken seriously")
            indications.warning(2)
            self.failed_flag = True
            return
        
        print("Line width = ", end-start)
        
        self.half_width = (end-start) // 2    
        
    def line_position(self):
        line = self.line_to_process
        line_start = line*self.height
        line_data = self.buf[line_start:line_start+self.width]
        
        # translate based on calibration
        x = line_data.translate(self.t)
        start = x.find(1)
        if start == -1:
            raise LostLineException

        # approximate the middle, but on calibration
        middle = start + self.half_width
        return middle - self.h_center
    