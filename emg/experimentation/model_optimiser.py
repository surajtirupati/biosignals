import os
import joblib
import warnings
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import train_test_split, GridSearchCV, ParameterGrid

from emg.data_ingestion.config import FEATURE_CONFIG
from emg.feature_extraction.feature_extraction import extract_features_from_files, prepare_data_for_training
import emg.models.model_suite as model_suite
from emg.models.model_suite import get_model

warnings.filterwarnings("ignore")


class Optimiser:
    def __init__(self, model_suite, model_save_tag):
        self.model_suite = model_suite
        self.tag = model_save_tag
        self.best_model = None
        self.best_params = None
        self.best_score = 0
        self.best_models = {}

    def save_model(self, model, model_name, save_dir='saved_models'):
        os.makedirs(save_dir, exist_ok=True)
        model_path = os.path.join(save_dir, f"{self.tag}_{model_name}_best_model.pkl")
        joblib.dump(model, model_path)

    def optimise_single_model(self, model_name, param_grid, X, y):
        model = get_model(model_name)
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy')
        grid_search.fit(X, y)

        best_model = grid_search.best_estimator_
        best_params = grid_search.best_params_
        best_score = grid_search.best_score_

        self.save_model(best_model, model_name)

        return best_model, best_params, best_score

    def optimise_multiple_models_model_lvl(self, model_configs, X, y):
        results = []

        for model_name, param_grid in model_configs.items():
            print(f"Optimising model: {model_name}...")
            best_model, best_params, best_score = self.optimise_single_model(model_name, param_grid, X, y)

            # Print the best model, params, and score for the current model
            print("\n\nBest Model: ", best_model)
            print("Best Params: ", best_params)
            print("Best Score: ", best_score)

            # Append results to the list
            results.append((model_name, best_model, best_params, best_score))
            self.best_models[model_name] = best_model

            # Update the overall best model if the current model's score is higher
            if best_score > self.best_score:
                self.best_model = best_model
                self.best_params = best_params
                self.best_score = best_score

        return results

    def optimise_multiple_models_param_lvl(self, model_configs, X, y):
        results = []

        # Splitting the dataset for training and evaluation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        for model_name, param_grid in model_configs.items():
            print(f"Optimising model: {model_name}...")

            # Iterate over all possible parameter combinations
            for params in ParameterGrid(param_grid):
                model = get_model(model_name, custom_params=params)
                model.fit(X_train, y_train)

                # Evaluate the model on the test set
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, average='weighted')

                # Append results
                results.append((model_name, model, params, accuracy, f1))

                # Print the evaluation metrics for each configuration
                print(f"Model: {model_name}, Params: {params}")
                print(f"Accuracy: {accuracy:.4f}, F1 Score: {f1:.4f}")

                # Check if this model is the best so far
                if accuracy > self.best_score:
                    self.best_model = model
                    self.best_params = params
                    self.best_score = accuracy

        return results

    def run_optimisation(self, config, X, y):
        results = self.optimise_multiple_models_model_lvl(config['model_configs'], X, y)
        return {
            "best_model": self.best_model,
            "best_params": self.best_params,
            "best_score": self.best_score,
            "results": results
        }

    def evaluate_best_model(self, X_train, X_test, y_train, y_test):
        self.best_model.fit(X_train, y_train)
        y_pred = self.best_model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        report = classification_report(y_test, y_pred)

        return {
            "accuracy": accuracy,
            "f1_score": f1,
            "classification_report": report,
            "best_params": self.best_params
        }

    def optimise(self, config, file_lists, labels, feature_config=FEATURE_CONFIG, test_size=0.1):
        # Extract features based on the feature config
        feature_sets = [extract_features_from_files(files, feature_config=feature_config) for files in file_lists]

        # Prepare the data
        X, y = prepare_data_for_training(feature_sets, labels)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

        # Run the optimisation process
        optimisation_results = self.run_optimisation(config, X_train, y_train)

        # Evaluate the best model found
        evaluation_results = self.evaluate_best_model(X_train, X_test, y_train, y_test)

        return {
            "optimisation_results": optimisation_results,
            "evaluation_results": evaluation_results
        }


# Example usage of the Optimiser class
if __name__ == "__main__":

    # tag for saving models
    tag = 'just_ssc'

    # Define your file lists and labels
    palm_files = ['palm_3min_21_27_11.csv']
    fist_files = ['fist_3min_21_22_24.csv']
    finger_files = ['f_you_21_35_48.csv']

    file_lists = [palm_files, fist_files, finger_files] # finger_files]
    labels = [0, 1, 2]  # 0 for palm, 1 for fist, 2 for finger
    test_size = 0.5

    optimiser = Optimiser(model_suite, tag)

    # Example configuration for optimisation
    config = {
        "model_configs": {
            "SVM": {"C": [0.1, 1, 10], "kernel": ["linear", "rbf"]},
            "RandomForest": {"n_estimators": [50, 100, 200], "max_depth": [None, 10, 20]},
            "ANN": {"hidden_layer_sizes": [(50,), (100,), (50, 50)], "activation": ["relu", "tanh"]},
            "LogisticRegression": {"C": [0.1, 1, 10], "solver": ["lbfgs", "liblinear"]},
            "NaiveBayes": {"var_smoothing": [1e-9, 1e-8, 1e-7]}
        }
    }

    # Run the optimisation
    results = optimiser.optimise(config, file_lists, labels, test_size=test_size)

    # Print out the results
    print("\n\nBest Model: ", optimiser.best_model)
    print("Best params:", results["evaluation_results"]["best_params"])
    print("Accuracy:", results["evaluation_results"]["accuracy"])
    print("F1 Score:", results["evaluation_results"]["f1_score"])
    print("Classification Report:\n", results["evaluation_results"]["classification_report"])

    print()
