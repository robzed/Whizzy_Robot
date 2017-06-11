'''
Created on 3 Jun 2017

@author: rob
'''

# See https://picamera.readthedocs.io/en/release-1.13/recipes1.html
# Consider numpy for these operations


try:
    from picamera import PiCamera
except ImportError:
    print("WARNING: importing stub PiCamera")
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
        #self.save_image("_test.bmp", test_img)

    def failed(self):
        return self.failed_flag

    def save_image(self, filename, img_data, bpp=8):
        save_image(filename, img_data, bpp, self.image_width, self.image_height)
    

        
    def start(self):
        # need to check field of view isn't compromised by rescale
        self.image_width = 320  # width should be /32
        self.image_height = 240 # height should be /16
        self.h_center = self.image_width // 2        # adjust this to adjust center of image
        
        self.line_to_process = self.image_height // 2
        self.line_to_calibrate = 90     # could be same as line to process... but test image...

        # test image 42 pixels, accept 66% size min, and 150% max
        track_line_width = int(self.image_width / 320 * 42)    # pixels (in center of image!) @ 320 pixels width
        line_follower_marker_width_in_mm = 19 # mm
        pixels_per_mm = track_line_width / line_follower_marker_width_in_mm      # pixels per mm
        self.marker_scan_offset_from_track = int(65 * pixels_per_mm) # 19mm/2 + 40mm before start + 80mm for marker long
        #end start marker to turn marker, max distance = 19+40+80+40+80 = 187mm, or 413 pixles (at 320 pixels width image)
        #ignoring distance change from camera to board

        min_fraction = 320 / (track_line_width*0.66)
        max_fraction = 320 / (track_line_width*1.5)
        self.minimum_width_of_follow_line_to_accept_during_calibrate = int(self.image_width / min_fraction)
        self.maximum_width_of_follow_line_to_accept_during_calibrate = int(self.image_width / max_fraction)
        self.near_right_edge = int((self.image_width // 16) * 15)
        self.near_left_edge = int(self.image_width // 16)

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
        #self.save_image("_yuv_convert.bmp", self.buf)
        
    def calibrate(self):
        if not self.started:
            self.start()
        
        indications.working(2)
        self.capture()
        self.calibrate_scan_line(self.line_to_calibrate)

    def create_test_image(self, mid_point):
        test_image = bytearray(self.image_height * self.image_width)
        for i in range(self.image_height * self.image_width):
            if self.buf[i] > mid_point:
                test_image[i] = 0
            else:
                test_image[i] = 255
        self.save_image("_level_based_output.bmp", test_image)

    def create_test_image2(self, mid_point, selected_line, name, left=None, right=None, found_pos=None):
        test_image = bytearray(self.image_height * self.image_width * 3)
        for i in range(self.image_height * self.image_width):
            if self.buf[i] > mid_point:
                test_image[i*3] = 0
                test_image[i*3+1] = 0
                test_image[i*3+2] = 0
            else:
                test_image[i*3] = 120
                test_image[i*3+1] = 120
                test_image[i*3+2] = 120
        selected_line *= 3 * self.image_width
        for i in range(self.image_width):
            test_image[selected_line + i*3] *= 2
            test_image[selected_line + i*3+1] *= 2
            test_image[selected_line + i*3+2] *= 2                    
        
        if left is None:
            left = (self.image_width//2 - self.marker_scan_offset_from_track)
        lcolumn = 3 * left
        if right is None:
            right = (self.image_width//2 + self.marker_scan_offset_from_track)        
        rcolumn = 3 * right
        for h in range(self.image_height):
            line = h * 3 * self.image_width
            if right > 0 and right < self.image_width:
                test_image[line + rcolumn] = 255
                test_image[line + rcolumn+1] = 0
                test_image[line + rcolumn+2] = 0
            if left >= 0 and left < self.image_width:
                test_image[line + lcolumn] = 0
                test_image[line + lcolumn+1] = 0
                test_image[line + lcolumn+2] = 255
                
        if found_pos  is not None:
            found_pos *= 3
            for h in range(self.image_height):
                line = h * 3 * self.image_width
                test_image[line + found_pos] = 0
                test_image[line + found_pos+1] = 255
                test_image[line + found_pos+2] = 0
            
            
        self.save_image(name, test_image, bpp=24)

        
    def calibrate_scan_line(self, line):
        line_start = line * self.image_width
        line_data = self.buf[line_start : (line_start+self.image_width)]

        low = min(line_data)
        high = max(line_data)
        if high-low < 10:
            print("Not enough contrast to calibrate")
            self.failed_flag = True
            return
        
        self.high_low_diff = high - low
        mid = ((high - low) // 2) + low
        self.mid = mid
        
        #print line data for analysis
        #for i in line_data:
        #    print(i, end=',')
        #
        # save images for examination
        #self.create_test_image(mid)
        self.create_test_image2(mid, line, "_level_based_output_with_line.bmp")
        
        # validate that the mid is reasoanble for the whole line
        # calibrate is between start and end markers, which
        # means center line should be the only thing there
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
            self.failed_flag = True
            return

        # set up translation array
        in_ = bytearray(256)
        out = bytearray(256)
        for i in range(0, mid):
            in_[i] = i
            out[i] = 0
        for i in range(mid, 256):
            in_[i] = i
            out[i] = 1
        self.t = bytearray.maketrans(in_, out)
        
        # confirm that is ok for the current line
        x = line_data.translate(self.t)
        start = x.find(1)
        if start == -1:
            print("Couldn't find start of line")
            self.failed_flag = True
            return
        
        end = x.find(0, start)
        if end == -1:
            print("Couldn't find end of line")
            self.failed_flag = True
            return
        
        if end-start < self.minimum_width_of_follow_line_to_accept_during_calibrate:
            print("Line too narrow to be taken seriously during calibrate")
            self.failed_flag = True
            return
        if end-start > self.maximum_width_of_follow_line_to_accept_during_calibrate:
            print("Line too wide to be taken seriously during calibrate")
            self.failed_flag = True
            return

        self.follow_line_width = end-start
        self.follow_line_width_min = int(0.66 * (end-start))
        self.follow_line_width_max = int(1.5 * (end-start))
        print("Line width (measured, min,max) = ", end-start, self.follow_line_width_min, self.follow_line_width_max)
        
        #self.half_width = (end-start) // 2    

    def markers_present(self, line_pos):        
        line_pos = int((line_pos * self.h_center) + self.h_center)       # make absolute, not relative to center
        
        # At the moment markers use vertical lines. But that is wrong - they 
        # should start wide and slope in as a straight line - they are 
        # perspective lines.
        # This, of course, assumes a straight track, which it's not. 

        # Relative to the center sounded logical, but this is not great either.
        #left = line_pos - self.marker_scan_offset_from_track
        #right = line_pos + self.marker_scan_offset_from_track
        
        # always make it at the edge
        left = 15
        right = self.image_width - 15
        self.create_test_image2(self.mid, self.line_to_process, "_level_based_output_with_line2.bmp", left, right, line_pos)
        marker_left = False
        marker_right = False
        img_size = self.image_width*self.image_height
        # make sure they are one pixel in from edge, at least
        if left >= 1:
            left_column_data = self.buf[left:img_size:self.image_width]
            # translate based on calibration
            x = left_column_data.translate(self.t)
            end = 0
            while True:
                start = x.find(1, end)
                if start == -1:
                    break
                end = x.find(0, start)
                if end == -1:
                    end = self.image_height # no end means off bottom
                if end-start > 10:  # number of lines to succeed
                    marker_left = True
                    break

        if right < (self.image_width-1):
            right_column_data = self.buf[right:img_size:self.image_width]
            # translate based on calibration
            x = right_column_data.translate(self.t)
            end = 0
            while True:
                start = x.find(1, end)
                if start == -1:
                    break
                end = x.find(0, start)
                if end == -1:
                    end = self.image_height # no end means off bottom
                if end-start > 10:  # number of lines to succeed
                    marker_right = True
                    break
        
        return marker_left, marker_right
    
    #def line_position_worker_midlevel(self):
    def line_position(self):
        # Types of horizontal scan line result:
        # No white present
        # White center line
        # left marker + white center line
        # right marker + white center line
        # left marker + right marker + white center line  (3 start+ends)
        #
        # we can't rely on this function to detect left and right marker... because 
        # the frame rate might not be high enough - horizontal scan will be better
        line_start = self.line_to_process*self.image_width
        line_data = self.buf[line_start:line_start+self.image_width]
        
        # translate based on calibration
        x = line_data.translate(self.t)
        
        end = 0
        markers = []
        for _ in range(4):
            start = x.find(1, end)
            if start == -1:
                break
            markers.append(start)
            end = x.find(0, start)
            if end == -1:
                break
            markers.append(end)
        
        count = len(markers)
        if count == 0:
            return None
        elif count == 1:
            # start only
            preferred = 0
            markers.append(self.image_width)     # sythesize another one
        elif count == 2:
            # start and end
            preferred = 0
        elif count == 3:
            #start and end, start2...
            # right white is a poor choice since it's off the edge
            preferred = 0   # guess, but right white is off right edge!!!
            markers.append(self.image_width)     # sythesize another one
        elif count == 4:
            #start and end, start2..end2
            if markers[0] < self.near_left_edge:
                preferred = 2
            else:
                preferred = 0   # guess, but right is either ok, or near right edge (in which case left is better)
        elif count == 5:
            #start and end, start2..end2, start3...
            # right white is a poor choice since it's off the edge
            if markers[0] < self.near_left_edge:
                preferred = 2
            else:
                preferred = 0   # guess, but right is either ok, or near right edge (in which case left is better)

            markers.append(self.image_width)     # sythesize another one ... right one is a poor choice

        elif count == 6:
            #start and end, start2..end2, start3...end3
            # probably start 2 is the best first choice            
            preferred = 2
            
        else:
            # count 7 = start and end, start2..end2, start3...end3, start4...
            # count 8 = start and end, start2..end2, start3...end3, start4...end4
            # don't understand how to process these
            # could reject short blips
            return None

        w = markers[preferred+1] - markers[preferred]
        if w >= self.follow_line_width_min and w <= self.follow_line_width_max:
            return (markers[preferred] + w//2 - self.h_center) / self.h_center
        
        if count < 4:
            return None
        
        nextw = 2 - preferred
        w = markers[nextw+1] - markers[nextw]
        if w >= self.follow_line_width_min and w <= self.follow_line_width_max:
            return (markers[nextw] + w//2 - self.h_center) / self.h_center
        
        if count < 6:
            return None
        
        nextw = 4
        w = markers[nextw+1] - markers[nextw]
        if w >= self.follow_line_width_min and w <= self.follow_line_width_max:
            return (markers[nextw] + w//2 - self.h_center) / self.h_center
    
        return None
        
        '''        
        # unrolled loop version
        # translate based on calibration
        x = line_data.translate(self.t)
        start1 = x.find(1)
        if start1 == -1:
            return None
            #raise LostLineException     # should we just return None?
        end1 = x.find(0, start)
        if end1 != -1:
            start2 = x.find(1, end1)
            if start2 != -1:
                end2 = x.find(0, start2)
                if end != -1:
                start3 = x.find(1, end2)
                if start3 != -1:
                    end3 = x.find(0, start)
                    if end3 != -1:
                        start4 = x.find(1, end1)
                        if start2 == -1:
                            # unexpected 4th white area
                            return None
                        else:
                            start = start2
                            end = end2
                    else:
                        # might be left or right marker
                        pass
                else:
                    #
                    pass
            else:
                pass
        else:
            pass
        
        # approximate the middle, but on calibration
        middle = start + self.half_width
        return middle - self.h_center
        '''
    
    
    def line_position_worker_step_change(self):
        line_start = self.line_to_process*self.image_width
        line_data = self.buf[line_start:line_start+self.image_width]
        
        last_data = line_data[0]
        step_change_level = 5
        
        for data in line_data:
            if abs(last_data - data) > step_change_level:
                if last_data > data:
                    # step down
                    pass
                else:
                    # step up
                    pass
    
    #def line_position(self):
    #    return self.line_position_mid_level()
    #LineDetector.line_position = line_position_worker_midlevel
    #LineDetector.line_position = line_position_worker_step_change
    
    