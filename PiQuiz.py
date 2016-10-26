#/usr/bin/python
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

import RPi.GPIO as GPIO
import time
import pygame
import os

debug = 0

# Setup GPIO
GPIO.setmode(GPIO.BOARD)

# Init speaker and path to wav files
pygame.mixer.init()
wavpath = os.path.dirname(os.path.realpath(__file__))

# Define Lights and Buttons

Light = [0,1,2,3]
Button = [0,1,2,3]
Sound = [0,1,2,3]
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

print wavpath + "/4.wav"

# Moderator Button Number
Moderator = Button[0]

# Time in MS to ignore second button press

btn_delay_ms = 300
lockout = False

# Button Callback

def button_press(channel):
    global lockout
    
    if lockout:
        return
    try:
        i = Button.index(channel)
        lockout = True
        GPIO.output(Light[i], True)
        if (Sound[i]):
            Sound[i].play()

    except ValueError:
        return
    

# Initialize Player and Buttons

for i in range(len(Button)):
    GPIO.setup(Light[i], GPIO.OUT)
    GPIO.output(Light[i], False)
    GPIO.setup(Button[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    if Button[i] != Moderator:
        if debug:
            print "Init Button %i " % i
        GPIO.add_event_detect(Button[i],
                              GPIO.FALLING,
                              callback=button_press,
                              bouncetime=btn_delay_ms)

# Control Loop

try:
    x = 0
    while True:
        x = x + 1
        if debug:
            print "looping1... %s" % x
        GPIO.wait_for_edge(Moderator, GPIO.FALLING)
        GPIO.output(Light[Button.index(Moderator)], True)
        GPIO.wait_for_edge(Moderator, GPIO.RISING)
        for i in range(len(Light)):
            GPIO.output(Light[i], False)
        lockout = False

except KeyboardInterrupt:
    GPIO.cleanup()


