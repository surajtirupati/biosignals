import asyncio
import numpy as np
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds

# Let’s get this board connected and ready for action
def initialize_board():
    BoardShim.enable_dev_board_logger()  # Logging everything for debugging—don’t miss a thing
    params = MindRoveInputParams()
    board_id = BoardIds.MINDROVE_WIFI_BOARD.value
    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream()
    return board

# Here’s where the magic happens—pulling in real-time data
async def read_emg_data(board, sampling_rate, window_size=2):
    num_points = window_size * sampling_rate
    while True:
        if board.get_board_data_count() >= num_points:
            data = board.get_current_board_data(num_points)
            emg_channels = BoardShim.get_emg_channels(board.board_id)
            emg_data = data[emg_channels, :]
            await process_data(emg_data)
        await asyncio.sleep(0.1)  # Let’s give it a quick break to avoid overloading

# This is the placeholder where we’ll run our model
async def process_data(data):
    # Drop your model’s prediction code here
    # Something like: result = your_model.predict(data)
    print(f"Got a fresh batch of data: {data.shape}")
    await asyncio.sleep(0.5)  # Simulate some thinking time

async def main():
    board = initialize_board()
    sampling_rate = BoardShim.get_sampling_rate(BoardIds.MINDROVE_WIFI_BOARD.value)
    try:
        await read_emg_data(board, sampling_rate)
    except KeyboardInterrupt:
        print("Okay, let’s wrap it up.")
    finally:
        board.stop_stream()
        board.release_session()

if __name__ == "__main__":
    asyncio.run(main())
