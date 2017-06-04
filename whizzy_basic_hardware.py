#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Basic hardware file for 'Whizzy' - Line Follower Robot based on GoPiGo with Raspberry Pi.
# Intended to run on a Raspberry Pi on the actual robot.
# Doesn't include GoPiGo specific board or camera.
#
# Copyright (C) 2017 Rob Probin.
# All original work.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#
# As of May 2017, this project is hosted at https://github.com/robzed/Whizzy_Robot
# 
try:
    import RPi.GPIO as GPIO
except ImportError:
    from test_stubs import GPIO_stub as GPIO

#import time
from collections import deque
try:
    import smbus
except ImportError:
    from test_stubs import smbus_stub as smbus


# hardware definitions
Buzzer_Pin = 24
Switch1_Pin = 25
Switch2_Pin = 23
Switch3_Pin = 18

# for RPI version 1, use "_bus = smbus.SMBus(0)"
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    _bus = smbus.SMBus(1)
else:
    _bus = smbus.SMBus(0)

def turn_on_white_headlights():
    # all white LEDs on:
    _bus.write_byte_data(0x70,0x00,0x5a)

def turn_off_headlights():
    # all LEDs off
    _bus.write_byte_data(0x70,0x00,0x00)

def setup_headlights():
    # see Semtech SC620 data sheet to understand values
    # all LEDs off
    _bus.write_byte_data(0x70,0x00,0x00)
    # gain up
    _bus.write_byte_data(0x70,0x09,0x0f)
    # brightness of white LEDs up
    _bus.write_byte_data(0x70,0x02,0x32)
    _bus.write_byte_data(0x70,0x04,0x32)
    _bus.write_byte_data(0x70,0x05,0x32)
    _bus.write_byte_data(0x70,0x07,0x32)
    
def buzzer_on():
    #print('\a')
    GPIO.output(Buzzer_Pin, GPIO.HIGH)
    
def buzzer_off():
    GPIO.output(Buzzer_Pin, GPIO.LOW)

def read_switch(which_switch):
    return GPIO.input(which_switch)

switch1_state = None
switch2_state = None
switch3_state = None
event_queue = deque()
event_count = 0

def setup_switch_state():
    global switch1_state
    global switch2_state
    global switch3_state
    switch1_state = GPIO.input(Switch1_Pin)
    switch2_state = GPIO.input(Switch2_Pin)
    switch3_state = GPIO.input(Switch3_Pin)
                
def get_switch_event():
    global switch1_state
    global switch2_state
    global switch3_state
    global event_queue
    global event_count
    switch_input = GPIO.input(Switch1_Pin)
    if (switch_input != switch1_state):
        switch1_state = switch_input
        event_count += 1
        if switch_input:
            event_queue.append("1")
        else:
            event_queue.append("-1")

    switch_input = GPIO.input(Switch2_Pin)
    if (switch_input != switch2_state):
        switch2_state = switch_input
        event_count += 1
        if switch_input:
            event_queue.append("2")
        else:
            event_queue.append("-2")
            
    switch_input = GPIO.input(Switch3_Pin)
    if (switch_input != switch3_state):
        switch3_state = switch_input
        event_count += 1
        if switch_input:
            event_queue.append("3")
        else:
            event_queue.append("-3")

    if event_count:
        event_count -= 1
        return event_queue.popleft()

    return None


def setup_hardware():
    print("Setting up hardware")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(Buzzer_Pin, GPIO.OUT)
    GPIO.setup(Switch1_Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Switch2_Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Switch3_Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    #GPIO.add_event_detect(channel, GPIO.RISING, callback=my_callback, bouncetime=200)
    setup_switch_state()
    setup_headlights()
    print("Hardware setup complete")
