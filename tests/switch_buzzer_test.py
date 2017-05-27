#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Switch and Buzzer test file for 'Whizzy' - Line Follower Robot based on GoPiGo with Raspberry Pi.
# Intended to run on a Raspberry Pi on the actual robot.
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

import RPi.GPIO as GPIO
import time
 
Buzzer_Pin = 24
Switch1_Pin = 25
Switch2_Pin = 23
Switch3_Pin = 18

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
 
GPIO.setup(Buzzer_Pin, GPIO.OUT)
GPIO.setup(Switch1_Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Switch2_Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Switch3_Pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(Buzzer_Pin, GPIO.HIGH)
time.sleep(0.2)
GPIO.output(Buzzer_Pin, GPIO.LOW)

Switch1_State = None
Switch2_State = None
Switch3_State = None
while True:
    switch_input = GPIO.input(Switch1_Pin)
    if (switch_input != Switch1_State):
        Switch1_State = switch_input
        print("Switch 1 ", switch_input)
    switch_input = GPIO.input(Switch2_Pin)
    if (switch_input != Switch2_State):
        Switch2_State = switch_input
        print("Switch 2 ", switch_input)
    switch_input = GPIO.input(Switch3_Pin)
    if (switch_input != Switch3_State):
        Switch3_State = switch_input
        print("Switch 3 ", switch_input)

