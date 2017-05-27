#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Main Control file for 'Whizzy' - Line Follower Robot based on GoPiGo with Raspberry Pi.
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
import sys


def turn_on_ir_headlights():
    pass
def turn_on_white_headlights():
    pass
def turn_on_all_headlights():
    pass
def turn_off_headlights():
    pass

def buzzer_on():
    pass
def buzzer_off():
    pass
def read_switch(which_switch):
    return 0


def whizzy_main():
    pass

def cmd_main():
    if len(sys.argv) >= 2:
        if sys.argv[1] == "headlight_ir":
            turn_on_ir_headlights()
        elif sys.argv[1] == "headlight_white":
            turn_on_white_headlights()
        elif sys.argv[1] == "headlight_both":
            turn_on_all_headlights()
        elif sys.argv[1] == "headlight_off":
            turn_off_headlights()
        else:
            print("Unknown command line argument")
            sys.exit(-201)
        
    whizzy_main()


if __name__ == "__main__":
    cmd_main()

