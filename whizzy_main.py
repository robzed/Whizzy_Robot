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
import os

try:
    import gopigo
    SIMULATION = False
except ImportError:
    print("WARNING: importing gopigo_stub")
    from test_stubs import gopigo_stub as gopigo
    SIMULATION = True

import atexit
import whizzy_basic_hardware as hw

atexit.register(gopigo.stop) # Stop the motors when the program is over.

from line_detector import LineDetector
#from line_detector import LostLineException
#import whizzy_indications as indications
import time
import whizzy_indications as indications




frame_count = 0
# Switches:
#  * start / stop
#  * line followers / drag race
#  * Shutdown

go_switch = hw.Switch1_Pin          # opposite of go switch is stop
drag_switch = hw.Switch2_Pin        # opposite of drag is follow
shutdown_switch = hw.Switch3_Pin    # opposite of shutdown is run
last_frame_count = 0
stop_line_follow = False

def continue_check():
    # @todo: check battery?
    return not stop_line_follow and hw.read_switch(go_switch) and not hw.read_switch(shutdown_switch)

def periodic_process():
    # @todo: check battery?
    
    # if we haven't aquired the line recently, stop
    global frame_count
    global last_frame_count
    if last_frame_count == frame_count:
        stop_line_follow = True
        gopigo.stop()
    last_frame_count = frame_count

# Speed figures from GoPiGo, line_follow1.py
# Calibrate speed at first run
# 100 is good with fresh batteries 
# 125 for batteries with half capacity
fwd_speed = 110                     # Forward speed at which the GoPiGo should run.
                                    # If you're swinging too hard around your line
                                    # reduce this speed.
slight_turn_speed = int(.7*fwd_speed)
turn_speed = int(.7*fwd_speed)

def straight():
    gopigo.set_speed(fwd_speed)
    gopigo.fwd()

def veer_left():
    gopigo.set_right_speed(slight_turn_speed)
    gopigo.set_left_speed(fwd_speed)
    gopigo.fwd()
        
def turn_left():
    gopigo.set_speed(turn_speed)
    gopigo.left()
        
def veer_right():
    gopigo.set_right_speed(fwd_speed)
    gopigo.set_left_speed(slight_turn_speed)
    gopigo.fwd()

def turn_right():
    gopigo.set_speed(turn_speed)
    gopigo.right()

direction_lookup = [
                    turn_left, #0
                    turn_left, #1
                    turn_left, #2
                    veer_left, #3
                    veer_left, #4
                    veer_left, #5
                    veer_left, #6
                    veer_left, #7
                    straight, #8
                    straight, #9
                    
                    straight, #10
                    
                    straight, #11
                    straight, #12
                    veer_right, #13
                    veer_right, #14
                    veer_right, #15
                    veer_right, #16
                    veer_right, #17
                    turn_right, #18
                    turn_right, #19
                    turn_right, #20
                    ]

def analysis_result(position, turn_marker, start_stop_marker):
    global frame_count
    frame_count += 1
    # We could use the GoPiGo line follower:
    #   https://www.dexterindustries.com/GoPiGo/gopigo-line-follower-getting-started/using-gopigo-line-follower/
    #   https://github.com/DexterInd/GoPiGo/tree/master/Software/Python/line_follower
    #   https://github.com/DexterInd/GoPiGo/blob/master/Software/Python/line_follower/line_follow1.py
    #
    # We probably want to use some sort of PID controller to set the wheel speeds
    if not stop_line_follow:
        position += 1   # change range to 0 to 2, mid 1
        position *= 10  # now it' 0 to 20, 10 center.
        # actually slightly biased...
        position = int(position)    # integer
        # make the move
        #direction_lookup[position]()
    
def video_frame_control():
    hw.turn_on_white_headlights()
    ld = LineDetector(0.25, continue_check, periodic_process, analysis_result)
    
    ld.start()
    try:
        ld.calibrate()
        if ld.failed():
            print("Camera Calibration Failed")
            indications.warning(2)
        else:
            global last_frame_count
            last_frame_count = -1   # give it time to find the line again
            global stop_line_follow
            stop_line_follow = False    # don't stop yet
            start = time.perf_counter()
            ld.video_capture()
            end = time.perf_counter()
            print("Total Capture time =%.2s" % (end - start))
            print("Total frame = %i" % frame_count)
            print("Frames per second = %.2f" % frame_count / (end - start))
    finally:
        ld.stop()        
    indications.finished()
    hw.turn_off_headlights()
    print("Finished")

def single_frame():
    hw.turn_on_white_headlights()
    ld = LineDetector(0.5, continue_check, periodic_process, analysis_result)
    
    ld.start()
    try:
        ld.calibrate()
        if ld.failed():
            print("Camera Calibration Failed")
            indications.warning(2)
        else:
            #if True:
            while hw.read_switch(hw.Switch1_Pin):
                start = time.perf_counter()
                ld.capture_one()
                end = time.perf_counter()
                print("Cap=%.1f ms" % (1000 * (end - start)))
                start = time.perf_counter()
                pos = ld.line_position()
                if pos is not None:
                    turn_marker, start_stop_marker = ld.markers_present(pos)
                end = time.perf_counter()
                print("Process=%.1f ms" % (1000 * (end - start)))
                print("Pos =", pos)
                print(turn_marker, start_stop_marker)
                time.sleep(0.5)
            #except LostLineException:
            #    print("Not found")
        indications.finished()
    finally:
        ld.stop()
        
    hw.turn_off_headlights()
    print("Finished")

def whizzy_main():
    led_mode = False
    led_count = 0
    indications.awake()
    while not hw.read_switch(shutdown_switch):
        time.sleep(0.2)
        if hw.read_switch(go_switch) or SIMULATION:
            gopigo.led_on(0)
            gopigo.led_off(0)
            video_frame_control()
            # single_frame()
            time.sleep(0.4)

        if not SIMULATION:
            # visual indication that we are running
            led_count += 1
            if led_count == 5:
                led_count = 0
                led_mode = not led_mode
                if led_mode == 0:
                    gopigo.led_on(0)
                    gopigo.led_off(1)
                else:
                    gopigo.led_on(1)
                    gopigo.led_off(0)
    
    indications.quitting()
    
def cmd_main():
    print("Welcome to Whizzy")
    hw.setup_hardware()
    print("Currently", gopigo.volt(), "volts")
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == "shutdown_on_exit":
            whizzy_main()
            print("Shutdown Raspberry Pi now!")
            
            os.system("sudo poweroff")
        elif cmd == "Hon":
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
        elif cmd == "switches":
            print("Go (Stop) switch", hw.read_switch(go_switch))
            print("Shutdown (Run) switch", hw.read_switch(shutdown_switch))
            print("Drag (Follow) switch", hw.read_switch(drag_switch))
        else:
            print("Unknown command line argument")
            sys.exit(-201)

        return
        
    whizzy_main()

if __name__ == "__main__":
    cmd_main()

