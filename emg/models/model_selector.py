import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from emg.feature_extraction.feature_extractor import extract_features_from_files, prepare_data_for_training
from emg.models.model_suite import get_model

def train_and_evaluate_model(file_lists, labels, model_name, custom_params=None, test_size=0.1):
    feature_sets = [extract_features_from_files(files) for files in file_lists]

    X, y = prepare_data_for_training(feature_sets, labels)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    model = get_model(model_name, custom_params)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    return {
        "accuracy": accuracy,
        "report": report
    }


if __name__ == '__main__':
    # Define your file lists and labels
    palm_files = ['palm_3min_21_27_11.csv']
    fist_files = ['fist_3min_21_22_24.csv']
    finger_files = ['f_you_21_35_48.csv']

    # Combine into a list of lists
    files = [palm_files, fist_files, finger_files]
    label_list = [0, 1, 2]  # 0 for palm, 1 for fist, 2 for finger

    # Train and evaluate the model
    results = train_and_evaluate_model(files, label_list, model_name="SVM", custom_params={"kernel": "linear"})

    # Print the results
    print(f"Accuracy: {results['accuracy']}")
    print(results['report'])
