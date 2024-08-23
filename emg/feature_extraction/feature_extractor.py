import numpy as np
from scipy.linalg import solve_toeplitz
from scipy.signal import welch

from emg.data_ingestion.config import ELECTRODE_CONFIG, SAMPLING_FREQ, WINDOW_LEN, OVERLAP, FEATURE_CONFIG
from emg.data_ingestion.data_loader import apply_window_csv, preprocess_data

def mean_absolute_value(emg_data):
    return np.mean(np.abs(emg_data), axis=1)

def root_mean_square(emg_data):
    return np.sqrt(np.mean(np.square(emg_data), axis=1))

def zero_crossing(emg_data, threshold=0.01):
    zc = np.sum(((emg_data[:, :-1] * emg_data[:, 1:]) < 0) & (np.abs(emg_data[:, :-1] - emg_data[:, 1:]) > threshold), axis=1)
    return zc

def slope_sign_changes(emg_data, threshold=0.01):
    diff_signal = np.diff(emg_data, axis=1)
    ssc = np.sum(((diff_signal[:, :-1] * diff_signal[:, 1:]) < 0) & (np.abs(diff_signal[:, :-1] - diff_signal[:, 1:]) > threshold), axis=1)
    return ssc

def waveform_length(emg_data):
    wl = np.sum(np.abs(np.diff(emg_data, axis=1)), axis=1)
    return wl

def integrated_emg(emg_data):
    return np.sum(np.abs(emg_data), axis=1)

def autoregressive_coefficients(emg_data, order=4):
    ar_coeffs = []
    for channel_data in emg_data:
        r = np.correlate(channel_data, channel_data, mode='full')
        r = r[len(r)//2:len(r)//2+order+1]
        r = r / r[0]
        ar_coeff = solve_toeplitz((r[:-1], r[:-1]), r[1:])
        ar_coeffs.append(ar_coeff)
    return np.array(ar_coeffs).flatten()

def hjorth_parameters(emg_data):
    activity = np.var(emg_data, axis=1)
    mobility = np.sqrt(np.var(np.diff(emg_data, axis=1), axis=1) / activity)
    complexity = np.sqrt(np.var(np.diff(np.diff(emg_data, axis=1), axis=1), axis=1) / np.var(np.diff(emg_data, axis=1), axis=1)) / mobility
    return np.vstack([activity, mobility, complexity]).T

def mean_frequency(emg_data, fs):
    freqs, psd = welch(emg_data, fs, axis=1)
    mean_freq = np.sum(freqs * psd, axis=1) / np.sum(psd, axis=1)
    return mean_freq

def median_frequency(emg_data, fs):
    freqs, psd = welch(emg_data, fs, axis=1)
    cumulative_sum = np.cumsum(psd, axis=1)
    median_freq = np.array([freqs[np.where(cumsum >= 0.5 * cumsum[-1])[0][0]] for cumsum in cumulative_sum])
    return median_freq

def power_spectral_density(emg_data, fs):
    freqs, psd = welch(emg_data, fs, axis=1)
    return psd

def spectral_entropy(emg_data, fs):
    freqs, psd = welch(emg_data, fs, axis=1)
    psd_norm = psd / np.sum(psd, axis=1, keepdims=True)
    spectral_ent = -np.sum(psd_norm * np.log2(psd_norm + np.finfo(float).eps), axis=1)
    return spectral_ent

### Extracting Features from files using config
def extract_features_multi_channel(emg_data_multi_channel, fs, config):
    features = []
    for channel_data in emg_data_multi_channel:

        channel_data = preprocess_data(channel_data, len(channel_data))
        channel_data = channel_data.reshape(1, -1)

        if config.get("mav", False):
            features.extend(mean_absolute_value(channel_data))
        if config.get("rms", False):
            features.extend(root_mean_square(channel_data))
        if config.get("zc", False):
            features.extend(zero_crossing(channel_data))
        if config.get("ssc", False):
            features.extend(slope_sign_changes(channel_data))
        if config.get("wl", False):
            features.extend(waveform_length(channel_data))
        if config.get("iemg", False):
            features.extend(integrated_emg(channel_data))
        if config.get("ar_coefficients", False):
            features.extend(autoregressive_coefficients(channel_data))
        if config.get("hjorth_parameters", False):
            features.extend(hjorth_parameters(channel_data))
        if config.get("mean_frequency", False):
            features.extend(mean_frequency(channel_data, fs))
        if config.get("median_frequency", False):
            features.extend(median_frequency(channel_data, fs))
        if config.get("psd", False):
            features.extend(power_spectral_density(channel_data, fs).flatten())  # Flatten PSD for simplicity
        if config.get("spectral_entropy", False):
            features.extend(spectral_entropy(channel_data, fs))
    return np.array(features)


def extract_features_from_file(filepath):
    emg_data = apply_window_csv(WINDOW_LEN, OVERLAP, filepath, ELECTRODE_CONFIG)
    full_features = [extract_features_multi_channel(sample_channels, SAMPLING_FREQ, FEATURE_CONFIG) for sample_channels in emg_data]
    return full_features

def extract_features_from_files(file_list, file_loc='../data'):
    all_features = []
    for file in file_list:
        file_path = f'{file_loc}/{file}'
        features = extract_features_from_file(file_path)
        all_features.extend(features)

    return all_features


if __name__ == '__main__':
    palm_files = ['palm_3min_21_27_11.csv']
    fist_files = ['fist_3min_21_22_24.csv']
    finger_files = ['f_you_21_35_48.csv']

    palm_features = extract_features_from_files(palm_files)
    fist_features = extract_features_from_files(fist_files)
    finger_features = extract_features_from_files(finger_files)

    print()
