'''
Created on 29 May 2017

@author: rob
'''

class SMBus():
    def __init__(self, bus):
        print("SMBus __init__:", bus)
        
    def write_byte_data(self, a, b, c):
        print("SMBus write data", a, b, c)
        
        