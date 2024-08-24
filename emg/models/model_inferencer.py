import pickle
import numpy as np

CLASS_LABELS = {0: 'palm', 1: 'fist', 2: 'finger'}


def load_model(model_path):
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    return model


def infer(model, input_data):
    if input_data.ndim == 1:
        input_data = input_data.reshape(1, -1)

    # Predict the class
    predicted_class = model.predict(input_data)

    # Map the predicted class to the gesture label
    return CLASS_LABELS[predicted_class[0]]


def main(model_path, input_data):
    # Load the model
    model = load_model(model_path)

    # Perform inference
    result = infer(model, input_data)

    # Output the result
    print(f"The predicted gesture is: {result}")


if __name__ == "__main__":
    # Example usage:
    sample_data = np.array([0.5, 0.3, -0.2, 0.1, 0.4, -0.3, 0.7, 0.2, 0.1, -0.4,
                            0.6, -0.1, 0.3, 0.2, -0.3, 0.4, 0.5, -0.2, 0.1, 0.4,
                            0.2, -0.5, 0.6, -0.4, 0.3, -0.2, 0.5, 0.1, 0.3, -0.1,
                            0.4, -0.3, 0.5, 0.2, -0.4, 0.3, 0.1, -0.5, 0.2, 0.4,
                            0.3, -0.2, 0.1, 0.5, -0.4, 0.2, 0.3, -0.1, 0.6, 0.4,
                            0.1, -0.3, 0.5, 0.2, 0.1, 0.3])
    path = 'path_to_your_model.pkl'

    main(path, sample_data)
