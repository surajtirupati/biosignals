from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB

# Hyperparameter definitions for each model
hyperparameters = {
    "SVM": {
        "C": 1.0,
        "kernel": "rbf",
        "gamma": "scale"
    },
    "RandomForest": {
        "n_estimators": 100,
        "max_depth": None,
        "min_samples_split": 2
    },
    "KNN": {
        "n_neighbors": 5,
        "weights": "uniform",
        "algorithm": "auto"
    },
    "ANN": {
        "hidden_layer_sizes": (100,),
        "activation": "relu",
        "solver": "adam",
        "max_iter": 200
    },
    "LogisticRegression": {
        "C": 1.0,
        "solver": "lbfgs",
        "max_iter": 100
    },
    "NaiveBayes": {
        "var_smoothing": 1e-9
    }
}


def get_model(model_name, custom_params=None):
    if model_name not in hyperparameters:
        raise ValueError(f"Model {model_name} not recognized. Available models: {list(hyperparameters.keys())}")

    params = hyperparameters[model_name]

    if custom_params:
        params.update(custom_params)

    if model_name == "SVM":
        return SVC(**params)
    elif model_name == "RandomForest":
        return RandomForestClassifier(**params)
    elif model_name == "KNN":
        return KNeighborsClassifier(**params)
    elif model_name == "ANN":
        return MLPClassifier(**params)
    elif model_name == "LogisticRegression":
        return LogisticRegression(**params)
    elif model_name == "NaiveBayes":
        return GaussianNB(**params)
    else:
        raise ValueError(f"Model {model_name} not recognized. Available models: {list(hyperparameters.keys())}")


if __name__ == '__main__':
    model_name = "SVM"
    model = get_model(model_name)

    custom_params = {"C": 0.5, "kernel": "linear"}
    model = get_model(model_name, custom_params)

    print()
