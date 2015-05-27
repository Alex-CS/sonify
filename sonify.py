#!/usr/bin/env python
# coding: utf-8
#
# Reads in the controller data and turns it into sound
#
# Author: Alex Simonides

from library.music import *

# Buttons / Joysticks
trigger_right = RT = "trigger_right"
trigger_left = LT = "trigger_left"
bumper_right = RB = "bumper_right"
bumper_left = LB = "bumper_left"
d_pad_up = DPU = "d_pad_up"
d_pad_down = DPD = "d_pad_down"
d_pad_left = DPL = "d_pad_left"
d_pad_right = DPR = "d_pad_right"
button_a = A = "button_a"
button_b = B = "button_b"
button_x = X = "button_x"
button_y = Y = "button_y"
analog_stick_right = RAS = "analog_right"
analog_stick_left = LAS = "analog_left"

presses = {
    RB: None,
    LB: None,
    A: None,
    B: None,
    X: None,
    Y: None,
}

parts = [
    Part(ACOUSTIC_BASS, 0),
    Part(STRING_ENSEMBLE2, 1),
    Part(ORCHESTRA_HIT, 2),
    Part(OBOE, 3),
    Part(TIMPANI, 4),
    Part(TREMOLO_STRINGS, 5),
]





def get_controller_input(fname):
    input_ = open(fname, "r")
    # parse input into a dictionary
    input_dict = {}

    input_.close()
    return input_dict

def compose_from_controller(input_dict):
    bpm = 120
    score = Score("Call of Duty Sonified", bpm)




def main():
    pass



if __name__ == "__main__":
    main()
