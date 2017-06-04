'''
Created on 4 Jun 2017

@author: rob
'''

import whizzy_basic_hardware as hw
import time

def working(time_in_seconds):
    while time_in_seconds > 0:
        hw.buzzer_on()
        time.sleep(0.01)
        time_in_seconds -= 0.01
        hw.buzzer_off()
        time.sleep(0.1)
        time_in_seconds -= 0.1        
    
    hw.buzzer_off()