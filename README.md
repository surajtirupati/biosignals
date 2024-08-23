# EEG Signal Processing and Classification Pipeline

This project involves the preprocessing, feature extraction, and classification of EEG signals using machine learning. The pipeline is designed to collect EEG data from a Neurosity EEG headset, preprocess the data to remove noise and artifacts, extract relevant features, and classify the signals using a Support Vector Machine (SVM) classifier.

## Table of Contents

- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Data Collection](#data-collection)
  - [Preprocessing](#preprocessing)
  - [Feature Extraction](#feature-extraction)
  - [Classification](#classification)
- [Configuration](#configuration)
- [Contributing](#contributing)

## Project Structure

The project is structured as follows:

- `collector_trial.py`: Script to collect raw EEG data from the Neurosity headset.
- `preprocessing.py`: Contains methods for preprocessing the raw EEG data.
- `feature_extraction.py`: Contains methods for extracting features from the preprocessed EEG data.
- `SVM.py`: Script for training and evaluating an SVM classifier on the extracted features.
- `windowing.py`: Contains methods for windowing the EEG data.
- `config/settings.py`: Contains configuration parameters for the project.
- `files/unfiltered/`: Directory to store collected raw EEG data.
- `.env`: Contains credentials for the Neurosity EEG headset (not included in the repository for security reasons).

## Installation

1. **Clone the repository**:

   ```sh
   git clone https://github.com/yourusername/eeg-pipeline.git
   cd eeg-pipeline
   ```

2. **Create and activate a virtual environment**:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   Create a `.env` file in the root directory with the following content:

   ```
   NEUROSITY_DEVICE_ID=your_device_id
   NEUROSITY_EMAIL=your_email
   NEUROSITY_PASSWORD=your_password
   ```

## Usage

### Data Collection

To collect raw EEG data using the Neurosity headset, run the `collector_trial.py` script:

```sh
python collector_trial.py
```

You will need to ensure your headset is on and streaming before running this. You also need to define the name of the JSON file you wish to store the resultant data in along with the time duration you want to record. This will save the collected data in the `files/unfiltered/` directory.

### Preprocessing

The preprocessing steps are defined in the `preprocessing.py` file. Each preprocessing step is a separate method:

- `bandpass_filter`
- `notch_filter`
- `baseline_correction`
- `remove_artifacts_ica`
- `epoching`
- `zscore_normalization`
- `downsample`

The `preprocess_eeg` method applies these steps based on the configuration specified in `config/settings.py`.

### Feature Extraction

The feature extraction methods are defined in the `feature_extraction.py` file. Features include:

- Power Spectral Density (PSD)
- Band Powers
- Peak Frequency
- Spectral Entropy
- Mean and Median Frequency
- Bandwidth
- Hjorth Parameters
- Spectral Flatness
- Statistical Features

The `extract_features_from_file` and `extract_features_from_files` methods handle feature extraction from single or multiple files.

### Classification

The `SVM.py` script trains and evaluates an SVM classifier on the extracted features:

```sh
python SVM.py
```

This script combines the extracted features, splits the data into training and testing sets, trains the SVM classifier, and evaluates its performance.

## Configuration

The configuration parameters are defined in `config/settings.py`:

- **Neurosity Credentials**:
  ```sh
  NEUROSITY_DEVICE_ID = os.getenv("NEUROSITY_DEVICE_ID")
  NEUROSITY_EMAIL = os.getenv("NEUROSITY_EMAIL")
  NEUROSITY_PASSWORD = os.getenv("NEUROSITY_PASSWORD")
  ```

- **Windowing Parameters**:
  ```sh
  WINDOW_LEN = 1
  OVERLAP = 0.5
  EPOCH_TIME = 0.0625
  SAMPLING_FREQ = 256
  DOWNSAMPLE_FREQ = 128
  ```

- **Electrode Configuration**:
  ```sh
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
  ```

- **Preprocessing Configuration**:
  ```sh
  preprocessing_config = {
      'bandpass': True,
      'notch': True,
      'baseline_correction': False,
      'z_score': True,
      'ICA_artefacts': True,
      'downsample': False
  }
  ```

- **Feature Extraction Configuration**:
  ```sh
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
  ```

## Contributing

Please feel free to fork and use this code for your own EEG-ML projects! Here is a link to Neurosity's homepage: https://neurosity.co
