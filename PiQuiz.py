#!/usr/bin/python
#
# Copyright (C) 2016 Jason Wessel
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


# Some notes:
#   If you were looking for a well written program, don't look here.
#   This program was written very quickly just to get the GPIOs tested
#   and working for a simple quiz game.  It should be refactored to not
#   use all these global variables and a more typical python style.
#
#   Discliamer aside, this is just a very basic 4 paddle lockout system
#   which has two modes.
#
#   Mode: Use Moderator Paddle
#      In this mode the moderator paddle must be pressed to clear
#      the lockout of one of the other 3 paddles
#   Mode: Timed Lockout Clear
#      In this mode the lockout clears automatically after a defined
#      interval and all 4 paddles are part of the lockout
#   Swithing modes:
#      The moderator paddle must be held down for 10 seconds in moderator
#      when in moderator mode.  In Timed Lockout Clear, the winning paddle
#      must be held down for 10 seconds and it will become the moderator
#      paddle.

import RPi.GPIO as GPIO
from time import sleep
import pygame
import os

debug = 0

# Startup mode is defined by use_moderator
#  The moderator paddle can change the game mode by pressing
#  it for "switch_time" milliseconds to the 4 paddle version
#  with a set clear_time
use_moderator = True
use_moderator = False
# Clear time is in ms
clear_time = 4000
# Time to hold moderator paddle before switching modes
switch_time = 10000

# Init speaker and path to wav files
pygame.mixer.init()
wavpath = os.path.dirname(os.path.realpath(__file__))

# Define Lights and Buttons

Light = [1,2,3,4]
Button = [1,2,3,4]
Sound = [1,2,3,4]
Light[0] = 15
Button[0] = 16
Sound[0] = pygame.mixer.Sound(wavpath + "/1.wav")
Light[1] = 32
Button[1] = 31
Sound[1] = pygame.mixer.Sound(wavpath + "/2.wav")
Light[2] = 35
Button[2] = 36
Sound[2] = pygame.mixer.Sound(wavpath + "/3.wav") 
Light[3] = 38
Button[3] = 37
Sound[3] = pygame.mixer.Sound(wavpath + "/4.wav")

# Moderator Button Number
Moderator = Button[1]
Winner = Moderator

# Time in MS to ignore second button press

btn_delay_ms = 300
lockout = False

# Button Callback

def button_press(channel):
    global lockout
    global Winner
    
    if lockout:
        return
    try:
        i = Button.index(channel)
        lockout = True
        Winner = channel
        GPIO.output(Light[i], True)
        if (Sound[i]):
            Sound[i].play()

    except ValueError:
        return
    

# Initialize Player and Buttons

def init_gpio():
    global debug
    global use_moderator
    global Moderator

    GPIO.setmode(GPIO.BOARD)

    for i in range(len(Button)):
        GPIO.setup(Light[i], GPIO.OUT)
        GPIO.output(Light[i], False)
        GPIO.setup(Button[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        if not (Button[i] == Moderator and use_moderator):
            if debug:
                print "Init Button %i " % i
            GPIO.add_event_detect(Button[i],
                                  GPIO.FALLING,
                                  callback=button_press,
                                  bouncetime=btn_delay_ms)

# Moderator Control Loop

def moderator_control_loop():
    global debug
    global lockout
    global use_moderator
    global switch_time
    global Moderator

    try:
        x = 0
        while True:
            x = x + 1
            if debug:
                print "looping1... %s" % x
            while GPIO.wait_for_edge(Moderator, GPIO.FALLING, timeout=100) is None:
                if not GPIO.input(Moderator):
                    break
                if debug:
                    print "looping2... %s %s" % (x, GPIO.input(Moderator))
            GPIO.output(Light[Button.index(Moderator)], True)
            tick = 0
            while GPIO.wait_for_edge(Moderator, GPIO.RISING, timeout=100) is None:
                tick = tick + 100
                if debug:
                    print "looping3... %s %s" % (x, GPIO.input(Moderator))
                if GPIO.input(Moderator):
                    break
                else:
                    if tick >= switch_time:
                        i = Button.index(Moderator)
                        if (Sound[i]):
                            Sound[i].play()
                        use_moderator = False
                        return 2;
            if debug:
                print "looping4... %s" % x
            for i in range(len(Light)):
                GPIO.output(Light[i], False)
            lockout = False

    except KeyboardInterrupt:
        return 0
    return 1

def clear_time_control_loop():
    global debug
    global lockout
    global use_moderator
    global clear_time
    global switch_time
    global Winner
    global Moderator

    try:
        x = 0
        tick = 0
        while True:
            sleep(0.1)
            if lockout:
                # Check if moderator paddle is depressed for
                # long enough to switch modes
                if not GPIO.input(Winner):
                    if debug:
                        print "Tick Moderator %s" % tick
                    if tick >= switch_time:
                        i = Button.index(Winner)
                        # What ever paddle kept the button down
                        # is the new Moderator
                        Moderator = Winner
                        if (Sound[i]):
                            Sound[i].play()
                        use_moderator = True
                        return 2;
                else:
                    # Process time out to reset
                    if debug:
                        print "Tick check %s" % tick
                    if tick >= clear_time:
                        for i in range(len(Light)):
                            GPIO.output(Light[i], False)
                        lockout = False
                        if debug:
                            print "Reseting paddles"
                        tick = 0
                tick = tick + 100


    except KeyboardInterrupt:
        return 0
    return 1

# Main Program
while True:
    init_gpio()
    if debug:
        print "Use Moderator: %s" % use_moderator
    if use_moderator:
        ret = moderator_control_loop()
    else:
        ret = clear_time_control_loop()
    GPIO.cleanup()
    if not ret:
        break
