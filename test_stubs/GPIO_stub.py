'''
Created on 29 May 2017

@author: rob
'''

_port_names = { 
               25: "Go/Stop switch",
               23: "Drag/Follow switch",
               18: "Run/Shutdown switch",
               24: "Buzzer",
               }

def _input(pin):
    print("read GPIO: input %i (%s)" % (pin, _port_names[pin]))
    #i = input("read GPIO: input %i (%s)" % (pin, _port_names[pin]))
    #if i == "1":
    #    return True
    return False

input = _input

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

