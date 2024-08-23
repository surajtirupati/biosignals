import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from eeg.classifier.feature_extraction import extract_features_from_files


freestyle_files = ['freestyling_1.json', 'freestyling_2.json', 'freestyling_3.json', 'freestyling_4.json']
silent_files = ['eyes_open_silent_1.json', 'eyes_open_silent_2.json', 'eyes_open_silent_3.json', 'eyes_open_silent_4.json']

all_freestyle_features = extract_features_from_files(freestyle_files)
all_silent_features = extract_features_from_files(silent_files)

# Create labels
labels_freestyle = np.zeros(len(all_freestyle_features))  # 0 for eyes open
labels_silent = np.ones(len(all_silent_features))  # 1 for eyes closed

# Combine features and labels
X = np.vstack((all_freestyle_features, all_silent_features))
y = np.hstack((labels_freestyle, labels_silent))

# Print the shape of X to understand its dimensions
print("Shape of feature matrix X:", X.shape)  # Should be (number of samples, number of features)

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Train the SVM classifier
svm_clf = SVC(kernel='linear')
svm_clf.fit(X_train, y_train)

# Predict and evaluate
y_pred = svm_clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print("Accuracy:", accuracy)
print("Classification Report:\n", report)
print("Done")
