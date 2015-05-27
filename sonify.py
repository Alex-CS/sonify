#!/usr/bin/env python
# coding: utf-8
#
# Reads in the controller data and turns it into sound
#
# Author: Alex Simonides

import re

from library.music import *

# CONTROLLER CONSTANTS -------------------------------------------------------

# Triggers / Joysticks
TRIGGER_LEFT = LT = "bLeftTrigger"
TRIGGER_RIGHT = RT = "bRightTrigger"
ANALOG_STICK_LEFT_X = LAX = "sThumbLX"
ANALOG_STICK_LEFT_Y = LAY = "sThumbLY"
ANALOG_STICK_RIGHT_X = RAX = "sThumbRX"
ANALOG_STICK_RIGHT_Y = RAY = "sThumbRY"
LA = "sThumbL"
RA = "sThumbR"

# Buttons
D_PAD_UP = DPU = "0x0001"
D_PAD_DOWN = DPD = "0x0002"
D_PAD_LEFT = DPL = "0x0004"
D_PAD_RIGHT = DPR = "0x0008"
BUMPER_LEFT = LB = "0x0100"
BUMPER_RIGHT = RB = "0x0200"
BUTTON_A = A = "0x1000"
BUTTON_B = B = "0x2000"
BUTTON_X = X = "0x4000"
BUTTON_Y = Y = "0x8000"
# there's 4 buttons we aren't mapping yet: start, back, and the analog clicks

# MUSIC_CONSTANTS ------------------------------------------------------------
BASE_ROOT = C4
BASE_DURATION = EN


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

    def _get_first_match(match_obj):
        """ Safely retrieve the first match. """
        try:
            return match_obj.group(1)
        except AttributeError or IndexError:
            return None

    def _intify(nonner):
        try:
            return int(nonner)
        except ValueError or TypeError:
            return 0

    # Read in the file and split it into sample chunks
    input_ = open(fname, "r")
    split_samples = filter(None, input_.read().split(delimiter))

    input_samples = []
    for i, raw_sample in enumerate(split_samples):
        def _find_match(label, match_group=catchall):
            return _get_first_match(re.search(base_pattern % (label, match_group),
                                              raw_sample))

        sample = {}
        # extract all the data and dump it into a dictionary
        raw_time = _find_match("Time", '"([^"]*)"')
        raw_buttons = _find_match("wButtons", '\[([^]]+)\]')

        sample['time'] = parse_time(raw_time)
        sample['buttons'] = set(filter(None, raw_buttons.split(","))
                                if raw_buttons else [])
        sample[LT] = _intify(_find_match(LT))
        sample[RT] = _intify(_find_match(RT))
        sample[LA] = (_intify(_find_match(LAX)),
                      _intify(_find_match(LAY)))
        sample[RA] = (_intify(_find_match(RAX)),
                      _intify(_find_match(RAY)))
        input_samples.append(sample)

    input_.close()
    return input_samples


def compose_from_samples(samples):
    """ Composes a musical score from the list of samples

    """
    root_pitch = BASE_ROOT
    duration = BASE_DURATION
    bpm = 120
    score = Score("The Sound Game", bpm)

    instruments = [
        Part(ACOUSTIC_BASS, 0),
        Part(STRING_ENSEMBLE2, 1),
        Part(ORCHESTRA_HIT, 2),
        Part(OBOE, 3),
        Part(TIMPANI, 4),
        Part(TREMOLO_STRINGS, 5),
    ]

    # Map each of our fun buttons to a list of notes
    button_pitch_sequences = {
        RB: [0, 2, 0, 3, 0, 4, 0, 5],
        LB: [7, 5, 7, 4, 7, 3, 7, 2],
        A: [5, 4, 3, 2, 4, -2, 1, 0],
        B: [7, 5, 6, 4, 5, 3, 2, 4],
        X: [2, 1, 0, 3, 4, 5, 6, 7],
        Y: [2, 1, 3, 2, 4, 3, 6, 7],
    }

    d_pad_buttons = [DPU, DPD, DPL, DPR]

    def _handle_d_pad(d_buttons, old_root=root_pitch):
        """ Change the root_pitch based in the d-pad input
            up/down - increase/decrease by one octave
            l/r - increase by one note
        """
        new_root = old_root
        steps = dict(zip(d_pad_buttons, [12, -12, -1, 1]))
        for direction in d_buttons:
            new_root = (new_root + steps.get(direction, 0)) % 127

        return new_root

    def _get_measure(timestamp):
        """ Use the timestamp of a sample to determine which
            measure to start the triggered phrase on.
        """
        # TODO: don't we need a start time to figure this out?
        return 0

    def _shift_to_root(sequence, root=root_pitch):
        """ Shifts all the pitches in the sequence to the given root pitch."""
        return map(lambda pitch: (pitch + root) % 127, sequence)

    for sample in samples:
        current_phrase_start = _get_measure(sample['time'])
        buttons = sample['buttons']
        directional_buttons = buttons.intersection(d_pad_buttons)
        note_buttons = buttons.intersection(button_pitch_sequences.keys())
        other_buttons = (buttons.difference(button_pitch_sequences)
                                .difference(d_pad_buttons))

        # tweak the root
        if directional_buttons:
            root_pitch = _handle_d_pad(directional_buttons, root_pitch)

        # loop through all the note buttons and add a phrase for each
        if note_buttons:
            pass

        # TODO: other buttons/interactions
        # ...

    score.addPartList(instruments)
    return score


def main():
    samples = parse_controller_input("test_input.txt")
    score = compose_from_samples(samples)


if __name__ == "__main__":
    main()
