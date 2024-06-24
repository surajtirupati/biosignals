import numpy as np
from scipy.signal import welch
from scipy.stats import skew, kurtosis, entropy
from config.settings import SAMPLING_FREQ, feature_config, WINDOW_LEN, OVERLAP
from classifier.windowing import apply_window
from classifier.preprocessing import preprocess_eeg


def hjorth_parameters(eeg_data):
    activity = np.var(eeg_data)
    mobility = np.sqrt(np.var(np.diff(eeg_data)) / activity)
    complexity = np.sqrt(np.var(np.diff(np.diff(eeg_data))) / np.var(np.diff(eeg_data))) / mobility
    return activity, mobility, complexity

def extract_frequency_features(eeg_data, fs, config):
    features = []
    freqs, psd = welch(eeg_data, fs, nperseg=fs*2) if config["psd"] else (None, None)

    if config["band_powers"]:
        bands = {'delta': (0.5, 4), 'theta': (4, 8), 'alpha': (8, 13), 'beta': (13, 30), 'gamma': (30, 50)}
        total_power = np.trapz(psd, freqs) if psd is not None else None
        for band, (low, high) in bands.items():
            band_power = np.trapz(psd[(freqs >= low) & (freqs <= high)], freqs[(freqs >= low) & (freqs <= high)]) if psd is not None else 0
            features.append(band_power)
            features.append(band_power / total_power if total_power else 0)
            if config["peak_frequency"]:
                band_freqs = freqs[(freqs >= low) & (freqs <= high)] if psd is not None else np.array([])
                band_psd = psd[(freqs >= low) & (freqs <= high)] if psd is not None else np.array([])
                peak_freq = band_freqs[np.argmax(band_psd)] if band_freqs.size > 0 else 0
                features.append(peak_freq)

    if config["spectral_entropy"]:
        features.append(entropy(psd / np.sum(psd)) if psd is not None else 0)

    if config["mean_median_frequency"]:
        mean_freq = np.sum(freqs * psd) / np.sum(psd) if psd is not None else 0
        cumulative_power = np.cumsum(psd) if psd is not None else np.array([])
        median_freq = freqs[np.where(cumulative_power >= cumulative_power[-1] / 2)[0][0]] if cumulative_power.size > 0 else 0
        features.extend([mean_freq, median_freq])

    if config["bandwidth"]:
        power_threshold = 0.5 * np.max(psd) if psd is not None else 0
        significant_bandwidth = freqs[psd >= power_threshold] if psd is not None else np.array([])
        bandwidth = significant_bandwidth[-1] - significant_bandwidth[0] if significant_bandwidth.size > 0 else 0
        features.append(bandwidth)

    if config["hjorth_parameters"]:
        activity, mobility, complexity = hjorth_parameters(eeg_data)
        features.extend([activity, mobility, complexity])

    if config["spectral_flatness"]:
        spectral_flatness = np.exp(np.mean(np.log(psd))) / np.mean(psd) if psd is not None else 0
        features.append(spectral_flatness)

    if config["statistical_features"]:
        features.extend([np.mean(eeg_data), np.var(eeg_data), skew(eeg_data), kurtosis(eeg_data)])

    return np.array(features)

def extract_features_multi_channel(eeg_data_multi_channel, fs, config):
    features = []
    for channel_data in eeg_data_multi_channel:
        channel_features = extract_frequency_features(channel_data, fs, config)
        features.extend(channel_features)
    return np.array(features)


def extract_features_multi_channel(eeg_data_multi_channel, fs, config):
    features = []
    for channel_data in eeg_data_multi_channel:
        channel_data = preprocess_eeg(channel_data, SAMPLING_FREQ)
        channel_features = extract_frequency_features(channel_data, fs, config)
        features.extend(channel_features)
    return np.array(features)


def extract_features_from_file(filepath):
    eeg_data = apply_window(WINDOW_LEN, OVERLAP, filepath)
    full_features = [extract_features_multi_channel(sample_channels, SAMPLING_FREQ, feature_config) for sample_channels in eeg_data]
    return full_features


def extract_features_from_files(file_list):
    all_features = []
    for file in file_list:
        file_path = f'../files/unfiltered/{file}'
        features = extract_features_from_file(file_path)
        all_features.extend(features)

    return all_features


if __name__ == '__main__':
    freestyle_files = ['freestyling_1.json', 'freestyling_2.json', 'freestyling_3.json', 'freestyling_4.json']
    silent_files = ['eyes_open_silent_1.json', 'eyes_open_silent_2.json', 'eyes_open_silent_3.json', 'eyes_open_silent_4.json']

    all_freestyle_features = extract_features_from_files(freestyle_files)
    all_silent_features = extract_features_from_files(silent_files)

    print()
