from dotenv import load_dotenv
import os

load_dotenv()

NEUROSITY_DEVICE_ID = os.getenv("NEUROSITY_DEVICE_ID")
NEUROSITY_EMAIL = os.getenv("NEUROSITY_EMAIL")
NEUROSITY_PASSWORD = os.getenv("NEUROSITY_PASSWORD")
WINDOW_LEN = 1
OVERLAP = 0.5
EPOCH_TIME = 0.0625
SAMPLING_FREQ = 256
DOWNSAMPLE_FREQ = 128

kinesis_setting = {
    'sensitivity': {
        'easy': 0.75,
        'medium': 0.825,
        'hard': 0.9
    },
    'thought': ['bitingALemon', 'leftArm']
}


channel_position_config = {
    'CP3': 0,
    'C3': 1,
    'F5': 2,
    'PO3': 3,
    'PO4': 4,
    'F6': 5,
    'C4': 6,
    'CP4': 7
}

electrode_config = {
    'CP3': True,
    'C3': True,
    'F5': True,
    'PO3': True,
    'PO4': True,
    'F6': True,
    'C4': True,
    'CP4': True
}

preprocessing_config = {
    'bandpass': True,
    'notch': True,
    'baseline_correction': False,
    'z_score': True,
    'ICA_artefacts': True,
    'downsample': False
}

feature_config = {
    "psd": True,
    "band_powers": True,
    "peak_frequency": True,
    "spectral_entropy": True,
    "mean_median_frequency": True,
    "bandwidth": True,
    "hjorth_parameters": True,
    "spectral_flatness": True,
    "statistical_features": True
}
