#!/usr/bin/env python
# coding: utf-8
#
# Reads in the controller data and turns it into sound
#
# Author: Alex Simonides

import re

from library.music import *

# Triggers / Joysticks
trigger_left = LT = "bLeftTrigger"
trigger_right = RT = "bRightTrigger"
analog_stick_left_x = LAX = "sThumbLX"
analog_stick_left_y = LAY = "sThumbLY"
analog_stick_right_x = RAX = "sThumbRX"
analog_stick_right_y = RAY = "sThumbRY"
LA = "sThumbL"
RA = "sThumbR"

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

def parse_time(time_string):
    # TODO fix this once we know the time format
    return time_string

def parse_controller_input(fname):
    """ Reads a log file and returns a list of dictionary samples
    that each look something like this:
    {
        "time": string,
        "buttons": list,
        LT: int,
        RT: int,
        LA: tuple,
        RA: tuple
    }
    """

    # RegEx setup
    base_pattern = r"%s: %s;"
    catchall = r"([^; ]+)"
    delimiter = '\n"$";\n'

    def get_first_match(match_obj):
        """ Safely retrieve the first match. """
        try:
            return match_obj.group(1)
        except AttributeError or IndexError:
            return None

    def intify(nonner):
        try:
            return int(nonner)
        except ValueError or TypeError:
            return 0

    # Read in the file and split it into sample chunks
    input_ = open(fname, "r")
    split_samples = filter(None, input_.read().split(delimiter))

    input_samples = []
    for i, raw_sample in enumerate(split_samples):
        def find_match(label, match_group=catchall):
            return get_first_match(re.search(base_pattern % (label, match_group),
                                              raw_sample))

        sample = {}
        # extract all the data and dump it into a dictionary
        raw_time = find_match("Time", '"([^"]*)"')
        raw_buttons = find_match("wButtons", '\[([^]]+)\]')

        sample['time'] = parse_time(raw_time)
        sample['buttons'] = filter(None, raw_buttons.split(",")) if raw_buttons else None
        sample[LT] = intify(find_match(LT))
        sample[RT] = intify(find_match(RT))
        sample[LA] = (intify(find_match(LAX)),
                      intify(find_match(LAY)))
        sample[RA] = (intify(find_match(RAX)),
                      intify(find_match(RAY)))
        input_samples.append(sample)

    input_.close()
    return input_samples

def compose_from_controller(input_dict):
    """ Composes a musical score from the list of samples

    """
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

    root = C4

    bpm = 120
    score = Score("Call of Duty Sonified", bpm)




def main():
    samples = parse_controller_input("test_input.txt")



if __name__ == "__main__":
    main()
