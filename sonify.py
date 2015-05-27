#!/usr/bin/env python
# coding: utf-8
#
# Reads in the controller data and turns it into sound
#
# Author: Alex Simonides

from library.music import *

# Triggers / Joysticks
trigger_left = LT = "bLeftTrigger"
trigger_right = RT = "bRightTrigger"
analog_stick_left_x = LAX = "sThumbLX"
analog_stick_left_y = LAY = "sThumbLY"
analog_stick_right_x = RAX = "sThumbRX"
analog_stick_right_y = RAY = "sThumbRY"

# Buttons
d_pad_up = DPU = "0x0001"
d_pad_down = DPD = "0x0002"
d_pad_left = DPL = "0x0004"
d_pad_right = DPR = "0x0008"
bumper_left = LB = "0x0100"
bumper_right = RB = "0x0200"
button_a = A = "0x1000"
button_b = B = "0x2000"
button_x = X = "0x4000"
button_y = Y = "0x8000"

instruments = [
    Part(ACOUSTIC_BASS, 0),
    Part(STRING_ENSEMBLE2, 1),
    Part(ORCHESTRA_HIT, 2),
    Part(OBOE, 3),
    Part(TIMPANI, 4),
    Part(TREMOLO_STRINGS, 5),
]

# Map each button to a list of notes
note_lists = {
    RB: [0, 2, 0, 3, 0, 4, 0, 5],
    LB: [7, 5, 7, 4, 7, 3, 7, 2],
    A: [5, 4, 3, 2, 4, -2, 1, 0],
    B: [7, 5, 6, 4, 5, 3, 2, 4],
    X: [2, 1, 0, 3, 4, 5, 6, 7],
    Y: [2, 1, 3, 2, 4, 3, 6, 7],
}


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
