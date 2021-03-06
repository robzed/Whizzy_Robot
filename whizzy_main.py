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



periodic_interval = 0.25
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
frame_lost_count_max = int(10 * (1/periodic_interval))
frame_lost_count = frame_lost_count_max
battery_count_max = int(5 * (1/periodic_interval))
battery_count = 10
drag_race = False
delayed_stopping = False
ignore_first_start_marker = False
ignore_first_start_marker_found = False
frame_rate_map = {}

def continue_check():
    # @todo: check battery?
    result = not stop_line_follow and hw.read_switch(go_switch) and not hw.read_switch(shutdown_switch)
    
    global ignore_first_start_marker
    global ignore_first_start_marker_found
    if ignore_first_start_marker_found and not gopigo.read_enc_status():
        ignore_first_start_marker = False
        ignore_first_start_marker_found = False
        print("Finished ignoring start")

    global delayed_stopping
    if delayed_stopping:
        result = result and gopigo.read_enc_status()

    return result


def periodic_process():
    # @todo: check battery?
    
    # if we haven't aquired the line recently, stop
    global frame_count
    global last_frame_count
    global frame_lost_count
    number_frames = frame_lost_count - last_frame_count
    global frame_rate_map
    if number_frames in frame_rate_map:
        frame_rate_map[number_frames] += 1
    else:
        frame_rate_map[number_frames] = 1
    
    # check for no video
    if last_frame_count == frame_count:
        print("No video received for", periodic_interval)
        gopigo.stop()
        
        global stop_line_follow
        frame_lost_count -= 1
        if frame_lost_count <= 0:
                stop_line_follow = True
                print("Quitting, no video for a time")
    else:
        global frame_lost_count_max
        frame_lost_count = frame_lost_count_max

    global battery_count
    global battery_count_max
    battery_count -= 1
    if battery_count <= 0:
        battery_count = battery_count_max
        print("Battery", gopigo.volt(), "volts")
        
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

def test_analysis(position, turn_marker, start_stop_marker):
    global frame_count
    frame_count += 1
    if frame_count % 30 == 0:
        print("%.3f %s %s" % (position, turn_marker, start_stop_marker))

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
#        position += 1   # change range to 0 to 2, mid 1
#        position *= 10  # now it' 0 to 20, 10 center.
#        # actually slightly biased...
#        position = int(position)    # integer
#        # make the move
#        direction_lookup[position]()

        # The speed of the GoPiGo can be between 0-255. The default speed is 200.
        # proportional control
        
        # @todo: investigate constants here ... effectively proportional constant
        position *= 0.5 # scale position to be less brutal to speed, to see if that helps
        
        if position < 0:
            other_speed = int(fwd_speed * (1+position))
            gopigo.set_left_speed(other_speed)
            gopigo.set_right_speed(fwd_speed)
        else:
            other_speed = int(fwd_speed * (1-position))
            gopigo.set_left_speed(fwd_speed)
            gopigo.set_right_speed(other_speed)
        
        gopigo.fwd()
        
        hw.buzzer_off()
        if turn_marker or start_stop_marker:
            # ignore first start/stop marker...
            # stop after past second start/stop marker
            
            global drag_race
            global delayed_stopping
            if drag_race or start_stop_marker:
                hw.buzzer_on()
                
                global ignore_first_start_marker
                global ignore_first_start_marker_found
                if not delayed_stopping and not ignore_first_start_marker_found:
                    
                    if ignore_first_start_marker:
                        ignore_first_start_marker_found = True
                    else:
                        delayed_stopping = True
            
                    # wheel diameter = 6cm (~18cm circumference)
                    # 2 wheel rotations = 36, 4 wheel rotations = 72
                    # number of encoder pulses to target (18 per rotation)
                    gopigo.enc_tgt(1,1,27)
                    gopigo.fwd()
            
                # todo:drag AND line follow - ignore first markers
            

def wait_for_go_to_set():
    while not hw.read_switch(go_switch):
        if hw.read_switch(shutdown_switch):
            break
        hw.buzzer_on()
        time.sleep(0.1)
        hw.buzzer_off()
        for _ in range(5):
            time.sleep(0.1)
            if hw.read_switch(go_switch):
                break


def video_frame_control(test_mode=False):
    hw.turn_on_white_headlights()
    if not test_mode:
        ld = LineDetector(periodic_interval, continue_check, periodic_process, analysis_result)
    else:
        ld = LineDetector(periodic_interval, continue_check, periodic_process, test_analysis)

    ld.start()
    try:
        ld.calibrate()
        if ld.failed():
            print("Camera Calibration Failed")
            indications.warning(2)
        else:
            global drag_race
            if drag_race:
                wait_for_go_to_set()
            global last_frame_count
            last_frame_count = -1   # give it time to find the line again
            global stop_line_follow
            stop_line_follow = False    # don't stop yet
            global delayed_stopping
            delayed_stopping = False    # not delayed yet
            global frame_rate_map
            frame_rate_map = {}

            global ignore_first_start_marker
            ignore_first_start_marker = True
            global ignore_first_start_marker_found
            ignore_first_start_marker_found = False

            start = time.perf_counter()
            ld.video_capture()
            end = time.perf_counter()
            print("Total Capture time =%.2s" % (end - start))
            print("Total frame = %i" % frame_count)
            print("Frames per second = %.2f" % (frame_count / (end - start)))
            print('Frame rate map')
            print(frame_rate_map)
    finally:
        ld.stop()
        gopigo.stop()   
        hw.turn_off_headlights()
    indications.finished()
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

def wait_for_switch_to_clear(which_switch):
    while hw.read_switch(which_switch):
        if which_switch != shutdown_switch and hw.read_switch(shutdown_switch):
            break
        hw.buzzer_on()
        time.sleep(0.1)
        hw.buzzer_off()
        for _ in range(5):
            time.sleep(0.1)
            if not hw.read_switch(which_switch):
                break

def whizzy_main():
    led_mode = False
    led_count = 0
    indications.awake()
    time.sleep(0.4)
    wait_for_switch_to_clear(go_switch)
    wait_for_switch_to_clear(drag_switch)

    while not hw.read_switch(shutdown_switch):
        time.sleep(0.2)
        drag_switch_state = hw.read_switch(drag_switch)
        if hw.read_switch(go_switch) or SIMULATION or drag_switch_state:

            global drag_race
            if drag_switch_state:
                drag_race = True
            else:
                drag_race = False
            gopigo.led_off(1)
            gopigo.led_off(0)
            video_frame_control()
            gopigo.stop()   # stop again ... just in case!
            # single_frame()
            wait_for_switch_to_clear(go_switch)
            wait_for_switch_to_clear(drag_switch)
            time.sleep(0.4)

        if not SIMULATION:
            # visual indication that we are running
            led_count += 1
            if led_count == 4:
                led_count = 0
                led_mode = not led_mode
                if led_mode == 0:
                    gopigo.led_on(0)
                    gopigo.led_off(1)
                else:
                    gopigo.led_on(1)
                    gopigo.led_off(0)
                    print("Battery", gopigo.volt(), "volts")
    
    indications.quitting()
    gopigo.led_off(1)
    gopigo.led_off(0)
    
def cmd_main():
    print("Welcome to Whizzy")
    hw.setup_hardware()
    print("Currently", gopigo.volt(), "volts")
    if len(sys.argv) >= 2:
        cmd = sys.argv[1]
        if cmd == "shutdown_on_exit":
            wait_for_switch_to_clear(shutdown_switch)
            whizzy_main()
            print("Shutdown Raspberry Pi now!")
            
            os.system("sudo poweroff")
        elif cmd == "forward":
            if len(sys.argv) >= 3:
                gopigo.set_speed(int(sys.argv[2]))
                gopigo.fwd()
                time.sleep(1)
            else:
                print("No speed")
        elif cmd == "veer":
            if len(sys.argv) >= 4:
                gopigo.set_left_speed(int(sys.argv[2]))
                gopigo.set_right_speed(int(sys.argv[3]))
                gopigo.fwd()
                time.sleep(4)
            else:
                print("No left speed, right speed ")
        elif cmd == "line":
            print("Requires Go set")
            video_frame_control(test_mode=True)
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
    print("Normal exit without shutdown")

if __name__ == "__main__":
    cmd_main()

