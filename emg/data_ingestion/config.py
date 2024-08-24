ELECTRODE_CONFIG = {
    'CH1': True,
    'CH2': True,
    'CH3': True,
    'CH4': True,
    'CH5': True,
    'CH6': True,
    'CH7': True,
    'CH8': True,
}

SAMPLING_FREQ = 500
WINDOW_LEN = 0.5
OVERLAP = 0.5

FEATURE_CONFIG = {
        "mean_absolute_value (mav)": False,
        "root_mean_square (rms)": False,
        "zero_crossing (zc)": False,
        "slope_sign_changes (ssc)": True,
        "waveform_length (wl)": False,
        "integrated_emg (iemg)": False,
        "autoregressive_coefficients (ar_coefficients)": False,
        "hjorth_parameters": False,
        "mean_frequency": False,
        "median_frequency": False,
        "power_spectral_density (psd)": False,
        "spectral_entropy": False
    }

