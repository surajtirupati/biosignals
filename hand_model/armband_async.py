import asyncio
from datetime import datetime
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
async def read_emg_data(board, sampling_rate, window_size=2, chunk_duration=0.1):
    chunk_size = int(sampling_rate * chunk_duration)  # Calculate the chunk size based on the chunk duration
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
                await process_data(emg_data)

        await asyncio.sleep(0.01)  # Check more frequently to reduce latency

# This is the placeholder where we’ll run our model
async def process_data(data):
    # Drop your model’s prediction code here
    # Something like: result = your_model.predict(data)
    await latency_test(data)
    print(f"Got a fresh batch of data: {data.shape}. Data:\n{data[0:10]}")
    await asyncio.sleep(0.5)  # Simulate some thinking time

async def latency_test(data):
    timestamp_channel = BoardShim.get_timestamp_channel(BoardIds.MINDROVE_WIFI_BOARD.value)
    timestamps = data[timestamp_channel, :]

    latencies = []
    for ts in timestamps:
        data_time = datetime.fromtimestamp(ts)
        current_time = datetime.now()
        latency = (current_time - data_time).total_seconds() * 1000  # Latency in milliseconds
        latencies.append(latency)

    # Optionally, you can process these latencies further or just print them
    for latency in latencies:
        print(f"Sample latency: {latency:.2f} ms")

    await asyncio.sleep(0.1)  # Slight delay to simulate async processing

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
