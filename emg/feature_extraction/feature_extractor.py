import numpy as np
from scipy.linalg import solve_toeplitz
from scipy.signal import welch

from emg.data_ingestion.config import ELECTRODE_CONFIG, SAMPLING_FREQ, WINDOW_LEN, OVERLAP, FEATURE_CONFIG
from emg.data_ingestion.data_loader import apply_window_csv, preprocess_data, preprocess_data_v2

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
    features = []
    for channel_data in emg_data_multi_channel:

        channel_data = preprocess_data(channel_data)
        channel_data = channel_data.reshape(1, -1)

        if np.isnan(channel_data).any():
            print("NaN in channel data!")

        if config.get("mav", False):
            mav = mean_absolute_value(channel_data)
            if np.isnan(mav).any():
                print("NaN detected in MAV feature!")
            features.extend(mav)

        if config.get("rms", False):
            rms = root_mean_square(channel_data)
            if np.isnan(rms).any():
                print("NaN detected in RMS feature!")
            features.extend(rms)

        if config.get("zc", False):
            zc = zero_crossing(channel_data)
            if np.isnan(zc).any():
                print("NaN detected in ZC feature!")
            features.extend(zc)

        if config.get("ssc", False):
            ssc = slope_sign_changes(channel_data)
            if np.isnan(ssc).any():
                print("NaN detected in SSC feature!")
            features.extend(ssc)

        if config.get("wl", False):
            wl = waveform_length(channel_data)
            if np.isnan(wl).any():
                print("NaN detected in WL feature!")
            features.extend(wl)

        if config.get("iemg", False):
            iemg = integrated_emg(channel_data)
            if np.isnan(iemg).any():
                print("NaN detected in IEMG feature!")
            features.extend(iemg)

        if config.get("ar_coefficients", False):
            ar_coeffs = autoregressive_coefficients(channel_data)
            if np.isnan(ar_coeffs).any():
                print("NaN detected in AR Coefficients feature!")
            features.extend(ar_coeffs)

        if config.get("hjorth_parameters", False):
            hjorth = hjorth_parameters(channel_data)
            if np.isnan(hjorth).any():
                print("NaN detected in Hjorth Parameters feature!")
            features.extend(hjorth)

        if config.get("mean_frequency", False):
            mean_freq = mean_frequency(channel_data, fs)
            if np.isnan(mean_freq).any():
                print("NaN detected in Mean Frequency feature!")
            features.extend(mean_freq)

        if config.get("median_frequency", False):
            median_freq = median_frequency(channel_data, fs)
            if np.isnan(median_freq).any():
                print("NaN detected in Median Frequency feature!")
            features.extend(median_freq)

        if config.get("psd", False):
            psd = power_spectral_density(channel_data, fs).flatten()
            if np.isnan(psd).any():
                print("NaN detected in PSD feature!")
            features.extend(psd)

        if config.get("spectral_entropy", False):
            spectral_entropy_val = spectral_entropy(channel_data, fs)
            if np.isnan(spectral_entropy_val).any():
                print("NaN detected in Spectral Entropy feature!")
            features.extend(spectral_entropy_val)

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
