import pandas as pd
import numpy as np
from math import ceil

from emg.data_ingestion.config import ELECTRODE_CONFIG
from emg.data_ingestion.preprocessing import log_transform_data


def preprocess_data(channel_data):
    channel_data = log_transform_data(channel_data)
    return channel_data

def normalize(df):
    return (df - df.mean()) / df.std()  # Simple Z-score normalization


def apply_window_csv(win_len, overlap, filepath, electrode_config, sampling_freq=500):
    df = pd.read_csv(filepath, sep=';', skiprows=1)
    selected_channels = [channel for channel, is_selected in electrode_config.items() if is_selected]

    # Calculate the number of samples per window and the number of samples for overlap
    samples_per_window = int(win_len * sampling_freq)
    overlap_samples = int(overlap * samples_per_window)
    non_overlap_samples = samples_per_window - overlap_samples

    # Calculate the number of windows
    total_samples = len(df)
    num_windows = ceil((total_samples - overlap_samples) / non_overlap_samples)

    windowing_output = []
    for i in range(num_windows):
        sample_output = [[] for _ in selected_channels]

        start_seg = i * non_overlap_samples
        end_seg = start_seg + samples_per_window

        if end_seg > total_samples:
            break

        window_data = df.iloc[start_seg:end_seg]

        for idx, channel in enumerate(selected_channels):
            sample_output[idx].extend(window_data[channel].values)

        output = np.array(sample_output)
        windowing_output.append(output)

    return windowing_output


if __name__ == '__main__':
    emg_data = apply_window_csv(1, 0.25, '../data/palm_3min_21_27_11.csv', ELECTRODE_CONFIG)
    print()
