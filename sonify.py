#!/usr/bin/env python
# coding: utf-8
#
# Reads in the controller data and turns it into sound
#
# Author: Alex Simonides

import re
import random

from music import *

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
TRIGGER_RANGE = (0, 255)
ANALOG_RANGE = (-32768, 32767)
ANALOG_SQUARED_RANGE = (ANALOG_RANGE[0] * ANALOG_RANGE[1], ANALOG_RANGE[0]**2)

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
MAX_MIDI_VALUE = 127


def parse_controller_output(fname):
    """ Reads a log file and returns a dictionary of samples (keyed to times)
    that each look something like this:
    {
        "buttons": list,
        LT: int,
        RT: int,
        LA: tuple,
        RA: tuple
    }
    """

    # RegEx setup
    base_pattern = r"%s: ?%s;"
    catchall = r"([^; ]+)"
    delimiter = '\n$;\n'

    def _get_first_match(match_obj):
        """ Safely retrieve the first match. """
        try:
            return match_obj.group(1)
        except AttributeError or IndexError:
            return None

    def _intify(nonner):
        """ Safely turn something into an int."""
        try:
            return int(nonner)
        except ValueError or TypeError:
            return 0

    # Read in the file and split it into sample chunks
    input_ = open(fname, "r")
    split_samples = filter(None, input_.read().split(delimiter))

    output_samples = {}
    for i in range(len(split_samples)):
        raw_sample = split_samples[i]
        def _find_match(label, match_group=catchall):
            return _get_first_match(re.search(base_pattern % (label, match_group),
                                              raw_sample))

        # extract all the data and dump it into a dictionary

        time = _intify(_find_match("Time"))
        sample = output_samples.get(time, {})
        raw_buttons = _find_match("wButtons", '\[([^]]+)\]')
        sample['buttons'] = set(filter(None, raw_buttons.split(","))
                                if raw_buttons else [])
        sample[LT] = _intify(_find_match(LT))
        sample[RT] = _intify(_find_match(RT))
        sample[LA] = (_intify(_find_match(LAX)),
                      _intify(_find_match(LAY)))
        sample[RA] = (_intify(_find_match(RAX)),
                      _intify(_find_match(RAY)))
        output_samples[time] = sample

    input_.close()
    print "Parsed samples"
    return output_samples


def map_value_ranges(value, old_range, new_range):
    """ Wraps the music library mapValue function to have fewer inputs."""
    if len(old_range) == len(new_range) == 2:
        return mapValue(value, old_range[0], old_range[1], new_range[0], new_range[1])
    else:
        return value

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
    pitch_sequences = [
        [0, 2, 0, 3, 0, 4, 0, 5],
        [7, 5, 7, 4, 7, 3, 7, 2],
        [5, 4, 3, 2, 4, 0, 1, 0],
        [7, 5, 6, 4, 5, 3, 2, 4],
        [2, 1, 0, 3, 4, 5, 6, 7],
        [2, 1, 3, 2, 4, 3, 6, 7],
    ]

    # FIXME: this function is only a placeholder so far
    def _get_start(timestamp):
        """ Use the timestamp of a sample to determine which
            measure to start the triggered phrase on.
        """
        # TODO: do we need a start time to figure this out?
        return 0

    def _shift_to_root(sequence, root=root_pitch):
        """ Shifts all the pitches in the sequence to the given root pitch."""
        return map(lambda pitch: (pitch + root) % MAX_MIDI_VALUE, sequence)

    def _combine_xy(analog_stick):
        """ Takes a tuple representing the x and y coordinates of an analog
            stick and merges them into one value for simpler scaling.
        """
        return analog_stick[0] * analog_stick[1]

    def add_notes_helper(phrase, pitches, durations):
        if not isinstance(durations, list):
            durations = [durations for i in xrange(len(pitches))]
        # make sure the lists match in length
        not_equal_len = cmp(len(pitches), len(durations))
        if not_equal_len:
            longer, shorter = (pitches, durations) if not_equal_len > 0 else (durations, pitches)
            for i in xrange(len(longer) - len(shorter)):
                shorter.append(shorter[i])
        phrase.addNoteList(pitches, durations)
        return phrase

    def _choose_part_for_phrase(analog, phrase):
        """ Maps the input into the range of our instruments to
            determine which one to add the phrase to.
        """
        sq_value = _combine_xy(analog)
        instrument = instruments[map_value_ranges(sq_value,
                                                  ANALOG_SQUARED_RANGE,
                                                  (0, len(instruments)-1))]
        instrument.addPhrase(phrase)

    sample_pairs = sorted(samples.items(), cmp=lambda x,y: cmp(x[0], y[0]))
    final_time_ms = sample_pairs[len(sample_pairs)-1][0]
    final_time_mins = final_time_ms / 60000.  # 1 min / 60000 ms
    beat_count = 2*floor(bpm * final_time_mins)

    beat_samples = [sample_pairs[i][1] for i in
                         xrange(0, len(sample_pairs), floor(len(sample_pairs) /
                                                            beat_count))]

    for i in xrange(len(beat_samples)):
        current_phrase = Phrase(i)
        sample = beat_samples[i]

        if len(sample["buttons"]) > 0:
            root_pitch = random.randint(40, 80)
        left_analog = sample[LA]
        right_analog = sample[RA]

        pitches = _shift_to_root(random.choice(pitch_sequences))
        durations = [EN for i in xrange(len(pitches))]
        current_phrase.addNoteList(pitches, durations)

        # Choose the instrument based on which segment of the circle the l-stick is
        theta = atan2(left_analog[1], left_analog[0])
        instrument_index = mapValue(theta, -pi, pi, 0, 5)
        instrument = instruments[instrument_index]

        instrument.setPan(map_value_ranges(right_analog[0], ANALOG_RANGE, (PAN_LEFT, PAN_RIGHT)))

        instrument.addPhrase(current_phrase)
        instruments[instrument_index] = instrument

    score.addPartList(instruments)
    return score


def main():
    samples = parse_controller_output("xboxdrv/output.txt")
    score = compose_from_samples(samples)
    View.sketch(score)
    Play.midi(score)
    Write.midi(score, "The_Sound_Game.mid")


if __name__ == "__main__":
    main()
