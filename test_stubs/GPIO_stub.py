'''
Created on 29 May 2017

@author: rob
'''

def input(pin):
    print("read GPIO: input", pin, "returning False")
    return False

RPI_REVISION = 1

def setmode(io_name_mode):
    print("GPIO: set mode", io_name_mode)
    
BCM = "Broadcom names"  # probably poor stub

def setwarnings(flag):
    print("GPIO: set warnings", flag)
    
PUD_UP = "Pulled up"
IN = "input"
OUT = "output"

def setup(pin, direction, pull_up_down=""):
    print("GPIO: setup pin", pin, direction, pull_up_down)


def output(pin_def, state):
    #print("Output", pin_def, state)
    pass

LOW = "0"
HIGH = "1"

