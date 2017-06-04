'''
Created on 4 Jun 2017

@author: rob
'''

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
        
        pass
    
    def start_preview(self, **options):
        pass
    
    def capture(self, output, format=None, use_video_port=False, resize=None, 
                splitter_port=0, bayer=False, **options):
        pass
    
    def capture_continuous(self, output, format=None, use_video_port=False, 
                           resize=None, splitter_port=0, burst=False, bayer=False, 
                           **options):
        pass
    
    
    def capture_sequence(self, outputs, format='jpeg', use_video_port=False, 
                     resize=None, splitter_port=0, burst=False, bayer=False, **options):
        pass

    def close(self):
        pass
    
