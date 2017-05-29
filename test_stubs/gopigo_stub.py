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

