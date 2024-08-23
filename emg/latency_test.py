import time
import numpy as np
from datetime import datetime
from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds

def initialize_board():
    BoardShim.enable_dev_board_logger()  # Logging for debugging
    params = MindRoveInputParams()
    board_id = BoardIds.MINDROVE_WIFI_BOARD.value
    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream()
    return board

def calculate_latency(timestamps):
    latencies = []
    for ts in timestamps:
        data_time = datetime.fromtimestamp(ts)
        current_time = datetime.now()
        latency = (current_time - data_time).total_seconds() * 1000  # Latency in milliseconds
        latencies.append(latency)
    return latencies

def main():
    board = initialize_board()
    sampling_rate = BoardShim.get_sampling_rate(BoardIds.MINDROVE_WIFI_BOARD.value)
    try:
        while True:
            num_points = 1  # Get the latest data point to check latency
            data = board.get_current_board_data(num_points)
            timestamp_channel = BoardShim.get_timestamp_channel(board.board_id)
            timestamps = data[timestamp_channel, :]
            latencies = calculate_latency(timestamps)
            for latency in latencies:
                print(f"Sample latency: {latency:.2f} ms")
            time.sleep(0.1)  # Slight delay between checks
    except KeyboardInterrupt:
        print("Stopping latency test.")
    finally:
        board.stop_stream()
        board.release_session()


if __name__ == "__main__":
    main()
