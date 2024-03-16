"""
processing_delay.py
----------------
by Mike Liao

Simulate the processing delay that exposes the race condition bug.
"""

import time
from datetime import datetime

LOG_FOLDER = './output'

def processing_delay():
    start_time = time.time()

    # Sample computation to simulate delay
    result = 0
    for i in range(10000):
        result += i*i

    end_time = time.time()

    elapsed_time = (end_time - start_time) * 1e6  # Convert to microseconds
    print(f"Elapsed time: {elapsed_time} microseconds")

def io_delay():
    timestamp = time.time()
    formatted_timestamp = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    # Simulate I/O delay
    with open(f"{LOG_FOLDER}/log_prize.txt", "w") as f:
        f.write(f"Prize claimed at {formatted_timestamp}\n")

if __name__ == "__main__":
    # processing_delay()
    start_time = time.time()
    io_delay()
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1e3  # Convert to microseconds
    print(f"Elapsed time: {elapsed_time} ms")