'''
Created on 29 May 2017

@author: rob
'''

import sys

def stop():
    print("gopigo: Stop")

def volt():
    print("gopigo: Voltage")
    return 14.0

def led_on(LED):
    if LED == 1:
        LED = "Left"
    elif LED == 0:
        LED = "Right"
        
    print("gopigo: LED on", LED)
    
def led_off(LED):
    if LED == 1:
        LED = "Left"
    elif LED == 0:
        LED = "Right"
    else:
        print("LED ERROR")
        sys.exit(1)
    print("gopigo: LED off", LED)

def set_speed(speed):
    print("Set speed", speed)

def set_right_speed(speed):
    print("Set right speed", speed)

def set_left_speed(speed):
    print("Set left speed", speed)
    
def fwd():
    print("Forward")
    
def left():
    print("Left")
    
def right():
    print("Right")
    
def read_enc_status():
    return 1        # 0=reached target

def enc_tgt(m1, m2, target):
    pass





    