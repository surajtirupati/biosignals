import json
import numpy as np
from math import ceil
from eeg.config.settings import channel_position_config, EPOCH_TIME, electrode_config


electrode_list = [channel_position_config[k] for k, v in electrode_config.items() if v]

def apply_window(win_len, overlap, filepath):
    with open(filepath) as handle:
        raw_original = json.loads(handle.read())
        raw = []
        for k, v in raw_original.items():
            raw.append(v)

    NO_EPOCHS = len(raw)
    TOTAL_SAMPLE_TIME = NO_EPOCHS * EPOCH_TIME
    WINDOW_RATIO = win_len / TOTAL_SAMPLE_TIME
    WINDOW_EPOCHS = WINDOW_RATIO * NO_EPOCHS
    OVERLAP_EPOCHS = overlap * WINDOW_EPOCHS
    NON_OVERLAP_EPOCHS = (1 - overlap) * WINDOW_EPOCHS
    ITERS = ceil(NO_EPOCHS - OVERLAP_EPOCHS) / (WINDOW_EPOCHS - OVERLAP_EPOCHS)

    windowing_output = []
    for i in range(0, ceil(ITERS)):
        sample_output = [[] for i in range(len(electrode_list))]

        start_seg = int(i * NON_OVERLAP_EPOCHS)
        end_seg = min(int(i * NON_OVERLAP_EPOCHS) + int(WINDOW_EPOCHS), NO_EPOCHS)
        first_sample = raw[start_seg:end_seg]

        for k in range(len(first_sample)):
            for idx, electrode in enumerate(electrode_list):
                channel = first_sample[k]['data'][electrode]
                sample_output[idx].extend(channel)

        output = np.array(sample_output)
        windowing_output.append(output)

    return windowing_output
