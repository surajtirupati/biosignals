import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.decomposition import PCA

def standardize_data(channel_data):
    scaler = StandardScaler()
    standardized_data = scaler.fit_transform(channel_data.reshape(-1, 1)).flatten()
    return standardized_data

def min_max_scale_data(channel_data):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(channel_data.reshape(-1, 1)).flatten()
    return scaled_data

def robust_scale_data(channel_data):
    scaler = RobustScaler()
    scaled_data = scaler.fit_transform(channel_data.reshape(-1, 1)).flatten()
    return scaled_data

def log_transform_data(channel_data):
    transformed_data = np.log1p(np.abs(channel_data))
    return transformed_data

def feature_wise_scaling(features):
    scaled_features = []
    for feature in features:
        if np.max(np.abs(feature)) > 0:
            scaled_feature = feature / np.max(np.abs(feature))
        else:
            scaled_feature = feature
        scaled_features.append(scaled_feature)
    return np.array(scaled_features)

def apply_pca(features, n_components=0.95):
    pca = PCA(n_components=n_components)
    pca_features = pca.fit_transform(features)
    return pca_features

def preprocess_data_v2(channel_data):
    # RMS Envelope
    window_size = len(channel_data)
    squared_signal = np.square(channel_data)
    window = np.ones(window_size) / float(window_size)
    rms_envelope = np.sqrt(np.convolve(squared_signal, window, 'same'))

    # Peak Dynamic Normalization
    peak_value = np.max(rms_envelope)
    if peak_value != 0:
        normalized_signal = rms_envelope / peak_value
    else:
        normalized_signal = rms_envelope

    # Ensure the values are between [0, 1]
    normalized_signal = np.clip(normalized_signal, 0, 1)

    return normalized_signal

def preprocess_data_v3(channel_data):
    peak_value = np.max(np.abs(channel_data))

    if peak_value > 0:
        normalized_signal = channel_data / peak_value
    else:
        normalized_signal = channel_data  # No normalization if peak_value is 0

    # Ensure the values are between [0, 1]
    normalized_signal = np.clip(normalized_signal, 0, 1)

    return normalized_signal
