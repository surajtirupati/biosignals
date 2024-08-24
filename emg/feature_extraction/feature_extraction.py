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

    total_power = np.sum(psd, axis=1)
    if np.any(total_power == 0):
        return np.zeros(psd.shape[0])

    mean_freq = np.sum(freqs * psd, axis=1) / total_power
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
    feature_functions = {
        "mean_absolute_value (mav)": mean_absolute_value,
        "root_mean_square (rms)": root_mean_square,
        "zero_crossing (zc)": zero_crossing,
        "slope_sign_changes (ssc)": slope_sign_changes,
        "waveform_length (wl)": waveform_length,
        "integrated_emg (iemg)": integrated_emg,
        "autoregressive_coefficients (ar_coefficients)": autoregressive_coefficients,
        "hjorth_parameters": hjorth_parameters,
        "mean_frequency": lambda x: mean_frequency(x, fs),
        "median_frequency": lambda x: median_frequency(x, fs),
        "power_spectral_density (psd)": lambda x: power_spectral_density(x, fs).flatten(),
        "spectral_entropy": lambda x: spectral_entropy(x, fs)
    }

    features = []
    for channel_data in emg_data_multi_channel:
        channel_data = preprocess_data(channel_data)
        channel_data = channel_data.reshape(1, -1)

        if np.isnan(channel_data).any():
            print("NaN in channel data!")

        for feature_name, is_enabled in config.items():
            if is_enabled:
                feature_function = feature_functions.get(feature_name)
                if feature_function:
                    feature_values = feature_function(channel_data)
                    if np.isnan(feature_values).any():
                        print(f"NaN detected in {feature_name} feature!")
                    features.extend(feature_values)

    return np.array(features)


def extract_features_from_file(filepath, feature_config=FEATURE_CONFIG, win_len=WINDOW_LEN, overlap=OVERLAP):
    emg_data = apply_window_csv(win_len, overlap, filepath, ELECTRODE_CONFIG)
    full_features = [extract_features_multi_channel(sample_channels, SAMPLING_FREQ, feature_config) for sample_channels in emg_data]
    return full_features

def extract_features_from_files(file_list, file_loc='../data', feature_config=FEATURE_CONFIG):
    all_features = []
    for file in file_list:
        file_path = f'{file_loc}/{file}'
        features = extract_features_from_file(file_path, feature_config=feature_config)
        all_features.extend(features)

    return all_features


def prepare_data_for_training(feature_sets, labels):
    X = np.vstack([np.vstack(features) for features in feature_sets])
    y = np.hstack([np.full(len(features), label) for features, label in zip(feature_sets, labels)])

    return X, y


if __name__ == '__main__':
    palm_files = ['palm_3min_21_27_11.csv']
    fist_files = ['fist_3min_21_22_24.csv']
    finger_files = ['f_you_21_35_48.csv']

    palm_features = extract_features_from_files(palm_files)
    fist_features = extract_features_from_files(fist_files)
    finger_features = extract_features_from_files(finger_files)

    X, y = prepare_data_for_training([palm_features, fist_features, finger_features], [0, 1, 2])

    print()
