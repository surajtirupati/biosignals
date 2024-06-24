import numpy as np
from scipy.signal import butter, filtfilt
from scipy.signal import iirnotch
from sklearn.decomposition import FastICA
from scipy.signal import resample
from config.settings import preprocessing_config as config
from config.settings import SAMPLING_FREQ, DOWNSAMPLE_FREQ

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, data)


def notch_filter(data, notch_freq, fs, quality_factor=30):
    nyquist = 0.5 * fs
    notch_freq = notch_freq / nyquist
    b, a = iirnotch(notch_freq, quality_factor)
    return filtfilt(b, a, data)


def baseline_correction(data):
    mean_value = np.mean(data)
    return data - mean_value


def remove_artifacts_ica(data, n_components=None):
    ica = FastICA(n_components=n_components, random_state=0)
    sources = ica.fit_transform(data.reshape(-1, 1))  # Reconstruct signals
    components = ica.mixing_
    # Here you would need to identify and remove the artifact components manually or via an algorithm.
    # For simplicity, let's assume we are retaining all components.
    reconstructed_signal = np.dot(sources, components.T)
    return reconstructed_signal.reshape(len(reconstructed_signal))


def epoching(data, epoch_length, fs):
    num_samples_per_epoch = int(epoch_length * fs)
    num_epochs = len(data) // num_samples_per_epoch
    epochs = np.array_split(data[:num_epochs * num_samples_per_epoch], num_epochs)
    return epochs


def zscore_normalization(data):
    mean = np.mean(data)
    std = np.std(data)
    return (data - mean) / std


def downsample(data, original_fs, target_fs):
    num_samples = int(len(data) * target_fs / original_fs)
    return resample(data, num_samples)


def preprocess_eeg(data, fs):
    # Apply bandpass filter
    if config['bandpass']:
        data = bandpass_filter(data, lowcut=0.5, highcut=50.0, fs=fs, order=5)

    # Apply notch filter to remove power line noise at 60Hz
    if config['notch']:
        data = notch_filter(data, notch_freq=60.0, fs=fs)

    # Apply baseline correction
    if config['baseline_correction']:
        data = baseline_correction(data)

    # Normalize the data using Z-score normalization
    if config['z_score']:
        data = zscore_normalization(data)

    # Apply ICA for artifact removal
    if config['ICA_artefacts']:
        data = remove_artifacts_ica(data, n_components=None)

    # Downsample the data to reduce computational load
    if config['downsample']:
        data = downsample(data, original_fs=SAMPLING_FREQ, target_fs=DOWNSAMPLE_FREQ)

    return data
