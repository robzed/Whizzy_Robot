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
try:
    import gopigo
except ImportError:
    from test_stubs import gopigo_stub as gopigo

import atexit
import whizzy_basic_hardware as hw

atexit.register(gopigo.stop) # Stop the motors when the program is over.

from line_detector import LineDetector
#from line_detector import LostLineException
#import whizzy_indications as indications
import time
import whizzy_indications as indications

def whizzy_main():
    ld = LineDetector()
    ld.calibrate()
    if ld.failed():
        print("Camera Calibration Failed")
        indications.warning(2)
    else:
        while True:
            try:
                start = time.perf_counter()
                ld.capture()
                print("Cap=%.1f ms" % (1000 * (time.perf_counter() - start)))
                start = time.perf_counter()
                pos = ld.line_position()
                if pos is not None:
                    turn_marker, start_stop_marker = ld.markers_present(pos)
                print("Process=%.1f ms" % (1000 * (time.perf_counter() - start)))
                print("Pos =", pos)
                print(turn_marker, start_stop_marker)
                time.sleep(0.2)
            #except LostLineException:
            #    print("Not found")
            finally:
                ld.stop()
        
        indications.finished()
    
def cmd_main():
    print("Welcome to Whizzy")
    hw.setup_hardware()
    print("Currently", gopigo.volt(), "volts")
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == "Hon":
            hw.turn_on_white_headlights()
        elif cmd == "Hoff":
            hw.turn_off_headlights()
        elif cmd == "buzz":
            hw.buzzer_on()
        elif cmd == "silence":
            hw.buzzer_off()
        elif cmd == "lledon":
            gopigo.led_on(1)
        elif cmd == "lledoff":
            gopigo.led_off(1)
        elif cmd == "rledon":
            gopigo.led_on(0)
        elif cmd == "rledoff":
            gopigo.led_off(0)
        else:
            print("Unknown command line argument")
            sys.exit(-201)
        
    whizzy_main()

if __name__ == "__main__":
    cmd_main()

