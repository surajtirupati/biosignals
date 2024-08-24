import numpy as np
import warnings

from sklearn.feature_selection import RFE, SequentialFeatureSelector
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from emg.data_ingestion.config import FEATURE_CONFIG
from emg.feature_extraction.feature_extractor import extract_features_from_files, prepare_data_for_training

warnings.filterwarnings("ignore")


class FeatureOptimiser:
    def __init__(self, model=None, n_features_to_select=None, direction='forward', scoring='accuracy', n_jobs=-1,
                 random_state=None):
        self.model = model if model is not None else RandomForestClassifier(random_state=random_state)
        self.n_features_to_select = n_features_to_select
        self.direction = direction
        self.scoring = scoring
        self.n_jobs = n_jobs
        self.random_state = random_state

    def recursive_feature_elimination(self, X, y):
        rfe = RFE(estimator=self.model, n_features_to_select=self.n_features_to_select)
        rfe.fit(X, y)
        selected_features = np.where(rfe.support_)[0]
        return selected_features, rfe

    def sequential_feature_selection(self, X, y):
        sfs = SequentialFeatureSelector(self.model, n_features_to_select=self.n_features_to_select,
                                        direction=self.direction, scoring=self.scoring, n_jobs=self.n_jobs)
        sfs.fit(X, y)
        selected_features = np.where(sfs.get_support())[0]
        return selected_features, sfs

    def permutation_feature_importance(self, X, y):
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=self.random_state)
        self.model.fit(X_train, y_train)
        baseline_score = accuracy_score(y_val, self.model.predict(X_val))

        perm_importance = permutation_importance(self.model, X_val, y_val, n_repeats=10, random_state=self.random_state,
                                                 n_jobs=self.n_jobs)
        importance_scores = perm_importance.importances_mean
        sorted_idx = np.argsort(importance_scores)[::-1]

        return sorted_idx, importance_scores

    def optimize_features(self, X, y, method='rfe'):
        """
        General method to perform feature optimization based on the chosen method.
        """
        if method == 'rfe':
            return self.recursive_feature_elimination(X, y)
        elif method == 'sfs':
            return self.sequential_feature_selection(X, y)
        elif method == 'permutation':
            return self.permutation_feature_importance(X, y)
        else:
            raise ValueError("Unsupported method. Choose 'rfe', 'sfs', or 'permutation'.")


def get_channel_and_feature(index, num_channels, feature_config=FEATURE_CONFIG):
    # Create a list of feature names based on the enabled features in the config
    feature_names_per_channel = [key for key, value in feature_config.items() if value]
    num_features_per_channel = len(feature_names_per_channel)

    # Calculate the total number of features across all channels
    total_features = num_channels * num_features_per_channel

    if index >= total_features:
        raise ValueError(f"Index {index} is out of range for the given configuration.")

    # Determine the channel number (1-based indexing)
    channel_number = (index // num_features_per_channel) + 1

    # Determine the feature index within the channel
    feature_index_within_channel = index % num_features_per_channel

    # Get the feature name from the config key
    feature_name = feature_names_per_channel[feature_index_within_channel]

    # Format channel name as "CH*"
    channel_name = f"CH{channel_number}"

    return channel_name, feature_name


def write_feature_report_to_file(rfe_mapped, sfs_mapped, perm_mapped, perm_scores, n, output_file="feature_report.txt"):
    with open(output_file, "w") as file:
        file.write("Feature Selection Report\n")
        file.write("=" * 80 + "\n\n")

        # RFE Section
        file.write("Top Features Selected by Recursive Feature Elimination (RFE)\n")
        file.write("-" * 80 + "\n")
        for idx, (channel, feature) in enumerate(rfe_mapped[:n]):
            file.write(f"{idx + 1}. {channel}: {feature}\n")
        file.write("\n")

        # SFS Section
        file.write("Top Features Selected by Sequential Feature Selection (SFS)\n")
        file.write("-" * 80 + "\n")
        for idx, (channel, feature) in enumerate(sfs_mapped[:n]):
            file.write(f"{idx + 1}. {channel}: {feature}\n")
        file.write("\n")

        # Permutation Importance Section
        file.write("Top Features Ranked by Permutation Importance\n")
        file.write("-" * 80 + "\n")
        for idx, (channel, feature) in enumerate(perm_mapped[:n]):
            file.write(f"{idx + 1}. {channel}: {feature} (Score: {perm_scores[sorted_features_perm[idx]]:.4f})\n")
        file.write("\n")

        file.write("=" * 80 + "\n")
        file.write("End of Report\n")


# Example usage
if __name__ == '__main__':

    report_name = ''
    num_channels = 8  # Assuming 8 channels

    palm_files = ['palm_3min_21_27_11.csv']
    fist_files = ['fist_3min_21_22_24.csv']
    finger_files = ['f_you_21_35_48.csv']

    palm_features = extract_features_from_files(palm_files, feature_config=FEATURE_CONFIG)
    fist_features = extract_features_from_files(fist_files, feature_config=FEATURE_CONFIG)
    finger_features = extract_features_from_files(finger_files, feature_config=FEATURE_CONFIG)

    X, y = prepare_data_for_training([palm_features, fist_features, finger_features], [0, 1, 2])

    n = 10
    feature_optimiser = FeatureOptimiser(n_features_to_select=n, random_state=42)

    # RFE example
    selected_features_rfe, rfe_model = feature_optimiser.optimize_features(X, y, method='rfe')

    # SFS example
    selected_features_sfs, sfs_model = feature_optimiser.optimize_features(X, y, method='sfs')

    # Permutation importance example
    sorted_features_perm, perm_scores = feature_optimiser.optimize_features(X, y, method='permutation')

    # Map the selected features to their corresponding channels and feature names
    rfe_mapped = [get_channel_and_feature(idx, num_channels, FEATURE_CONFIG) for idx in selected_features_rfe]
    sfs_mapped = [get_channel_and_feature(idx, num_channels, FEATURE_CONFIG) for idx in selected_features_sfs]
    perm_mapped = [get_channel_and_feature(idx, num_channels, FEATURE_CONFIG) for idx in sorted_features_perm]

    write_feature_report_to_file(rfe_mapped, sfs_mapped, perm_mapped, perm_scores, n, output_file=f'reports/{report_name}.txt')

    print(f"Selected features by RFE: {rfe_mapped}")
    print(f"Selected features by SFS: {sfs_mapped}")
    print(f"Feature ranking by permutation importance: {perm_mapped}")
    print(f"Permutation importance scores: {perm_scores}")

    print()
