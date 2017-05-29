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
import gopigo
import atexit
import whizzy_basic_hardware as hw

atexit.register(gopigo.stop) # Stop the motors when the program is over.


    
def whizzy_main():
    pass

def cmd_main():
    hw.setup_hardware()
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == "Lon":
            hw.turn_on_white_headlights()
        elif cmd == "Loff":
            hw.turn_off_headlights()
        elif cmd == "buzz":
            hw.buzzer_on()
        elif cmd == "silence":
            hw.buzzer_off()
        else:
            print("Unknown command line argument")
            sys.exit(-201)
        
    whizzy_main()

if __name__ == "__main__":
    cmd_main()

