'''
Created on 4 Jun 2017

@author: rob
'''
import struct
import sys
import os
from test_stubs.image_services import save_image

class RawImage():
    # for test purposes we convert jpeg images snapped with the camera into raw image sized
    # 320x240x24(RGB) with a 6 byte header in order to test processing.
    def __init__(self, filename):
        _, file_extension = os.path.splitext(filename)
        
        if file_extension == '.raw':
            # assume w16, h16, d16, RGB24 * w * h
            with open(filename, 'rb') as f:
                header = f.read(6)
                rgb_data = f.read()
    
            (self.width, self.height, self.depth) = struct.unpack(">HHH", header)
            #rgb_iterator = struct.iter_unpack('BBB', data)
            if self.height != 240 or self.width != 320 or self.depth != 24:
                print("Wrong sized RAW image")
                print(self.height, self.width, self.depth)
                sys.exit(1)

        #=======================================================================
        # elif file_extension == '.bmp':
        #     # very naive bitmap reader ... easily broken
        #     with open(filename, 'rb') as f:
        #         fileheader = f.read(14)
        #         infoheader= f.read(40)
        #         bgra_data = f.read()
        #     
        #     (type, fsize, reserved, offset) = struct.unpack('<2sLLL', fileheader)
        #     (hsize, w, h, planes, bpp, comp, isize, xppm, yppm, cct, icc) = struct.unpack('<LLLHHLLLLLL', infoheader)
        #     
        #     if type != b'BM':
        #         print("Header not BM")
        #         sys.exit(1)
        #     if offset != 14+40 or fsize != 14+40+len(rgb_data):
        #         print("Header sizes/offset unexpected")
        #         sys.exit(1)
        #     if hsize != 40:
        #         print("Header sizes unexpected")
        #         sys.exit(1)
        #     if self.h != 320 or self.w != 240 or self.bpp != 32:
        #         print("Wrong sized RAW image")
        #         print(self.height, self.width, self.depth)
        #         sys.exit(1)
        #     
        #     #need to resize bits per pixel and format from 
        #     #need to reverse lines
        #=======================================================================
        else:
            print("Unknown file extension", filename)
            sys.exit(1)
            
        #for x in range(self.width // 2):
        #    for y in range(self.height // 3):
        #        rgb_data[3 * (x + ((y * self.width)))] = 200
        
        save_image("image_as_loaded.bmp", rgb_data, self.depth, self.width, self.height)
        
        self.YUV420_data = self.Bitmap_to_Yuv420p(rgb_data, self.width, self.height)


    # RGB to YUV420 conversion
    # Not the fastest routine ever :-)
    # Based on https://stackoverflow.com/questions/9465815/rgb-to-yuv420-algorithm-efficiency#9467305
    # Original Author: Timbo (https://stackoverflow.com/users/1810/timbo)
    # No averaging of U and V for 2x2 pixel block. But that is ok, we don't use U and V here.
    #
    # Licensing:
    # This function is https://stackoverflow.blog/2009/06/25/attribution-required/ and 
    # https://creativecommons.org/licenses/by-sa/3.0/
    # GPLV3 compatibility: Short version: It's fine.
    #
    # GPLv3 Licensing Compatability Long version:
    # Because of Stackoverflow licensing (https://stackoverflow.com/help/licensing)
    # under Creative Commons Attribution-Share Alike, which points to Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0) 
    # which license allows 'or later version' https://creativecommons.org/licenses/by-sa/3.0/legalcode
    # which allows CC BY-SA 4.0 which is allows use in GPLv3 
    # https://wiki.creativecommons.org/wiki/ShareAlike_compatibility:_GPLv3
    # https://creativecommons.org/share-your-work/licensing-considerations/compatible-licenses/
    # https://wiki.creativecommons.org/wiki/ShareAlike_compatibility:_GPLv3#Option_to_comply_with_later_versions
    # https://www.fsf.org/blogs/licensing/creative-commons-by-sa-4-0-declared-one-way-compatible-with-gnu-gpl-version-3
    # Later versions of the GPL might or might no be compatible... see https://wiki.creativecommons.org/wiki/ShareAlike_compatibility:_GPLv3#Option_to_comply_with_later_versions
    # Note: originally I think Stackoverflow pointed at CC BY-SA 2.5, which also has the later version.
    # <Phew!>
    def Bitmap_to_Yuv420p(self, rgb, width, height):
        image_size = width * height
        upos = image_size;
        vpos = upos + upos // 4;
        i = 0;
        destination = bytearray(image_size + image_size//2)

        for line in range(height):
            if not (line %2):
                for _ in range(width//2):

                    r = rgb[3 * i]
                    g = rgb[3 * i + 1]
                    b = rgb[3 * i + 2]

                    destination[i] = ((66*r + 129*g + 25*b) >> 8) + 16
                    i += 1

                    destination[upos] = ((-38*r + -74*g + 112*b) >> 8) + 128
                    upos += 1
                    destination[vpos] = ((112*r + -94*g + -18*b) >> 8) + 128
                    vpos += 1

                    r = rgb[3 * i]
                    g = rgb[3 * i + 1]
                    b = rgb[3 * i + 2]

                    destination[i] = ((66*r + 129*g + 25*b) >> 8) + 16
                    i += 1
            else:
                for _ in range(width):
                    r = rgb[3 * i]
                    g = rgb[3 * i + 1]
                    b = rgb[3 * i + 2]
    
                    destination[i] = ((66*r + 129*g + 25*b) >> 8) + 16
                    i += 1

        return destination
    
    
class PiCamera_stub():
    '''
    Emulate PiCamera
    '''


    def __init__(self, camera_num=0, stereo_mode='none', stereo_decimate=False, 
                 resolution=None, framerate=None, sensor_mode=0, led_pin=None, 
                 clock_mode='reset', framerate_range=None):
        '''
        
        '''
        self.resolution = (1024, 768)
        self.test_image = RawImage("cam3i.raw")
    
    def start_preview(self, **options):
        pass
    
    def capture(self, output, format=None, use_video_port=False, resize=None, 
                splitter_port=0, bayer=False, **options):
        if resize[0] != 320 and resize[1] != 240:
            print("unexpected resize")
            sys.exit(1)
        if format != "yuv":
            print("Unexpected format")
            sys.exit(1)
            
        output[:] = self.test_image.YUV420_data
    
    def capture_continuous(self, output, format=None, use_video_port=False, 
                           resize=None, splitter_port=0, burst=False, bayer=False, 
                           **options):
        pass
    
    
    def capture_sequence(self, outputs, format='jpeg', use_video_port=False, 
                     resize=None, splitter_port=0, burst=False, bayer=False, **options):

        pass

    def close(self):
        pass
    
