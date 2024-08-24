import asyncio
import pickle
import numpy as np
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds

from emg.data_ingestion.config import FEATURE_CONFIG, WINDOW_LEN
from emg.models.model_inferencer import infer
from emg.realtime.latency_test import latency_test
from emg.feature_extraction.feature_extraction import extract_features_multi_channel

def initialize_board():
    BoardShim.enable_dev_board_logger()  # Logging everything for debugging—don’t miss a thing
    params = MindRoveInputParams()
    board_id = BoardIds.MINDROVE_WIFI_BOARD.value
    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream()
    return board

async def read_emg_data(board, sampling_rate, feature_config, model, window_size=WINDOW_LEN, chunk_duration=0.1):
    chunk_size = int(sampling_rate * chunk_duration)
    collected_data = []

    while True:
        if board.get_board_data_count() >= chunk_size:
            data_chunk = board.get_current_board_data(chunk_size)
            collected_data.append(data_chunk)

            # Combine chunks into one if the desired window size is reached
            if len(collected_data) * chunk_size >= window_size * sampling_rate:
                emg_channels = BoardShim.get_emg_channels(board.board_id)
                emg_data = np.hstack(collected_data)  # Combine the chunks
                collected_data = []  # Reset for the next batch

                await process_data(emg_data, model, feature_config)

        await asyncio.sleep(0.01)

async def process_data(data, model, feature_config=FEATURE_CONFIG):
    # Assuming data is in the format N_channels x N_samples
    features = extract_features_multi_channel(data, fs=500, config=feature_config)  # 500 is an assumed sampling rate
    result = infer(model, features)
    print(f"Predicted gesture: {result}")
    await latency_test(data)


async def main(model_path, feature_config=FEATURE_CONFIG, window_size=WINDOW_LEN):
    board = initialize_board()
    sampling_rate = BoardShim.get_sampling_rate(BoardIds.MINDROVE_WIFI_BOARD.value)

    # Load the model from the .pkl file
    with open(model_path, 'rb') as file:
        model = pickle.load(file)

    try:
        await read_emg_data(board, sampling_rate, feature_config, model, window_size)
    except KeyboardInterrupt:
        print("Okay, let’s wrap it up.")
    finally:
        board.stop_stream()
        board.release_session()


if __name__ == "__main__":
    path_to_model = '../experimentation/saved_models/just_rms_500ms/just_rms_LogisticRegression_best_model.pkl'
    asyncio.run(main(model_path=path_to_model))
