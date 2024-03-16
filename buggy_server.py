"""
buggy_server.py
----------------
by Mike Liao

Implements a vulnerable web server with a race condition bug.
"""

import threading
import os
import time

from flask import Flask, request

from processing_delay import io_delay, processing_delay
import socket

app = Flask(__name__)
SERVER_IP = '0.0.0.0'
SERVER_PORT = 25632
PROCESSING_DELAY = 0.3 / 1000  # 0.3 ms

# Global counter
mutex = threading.Lock()
TOTAL_PRIZES = 1
num_prizes = TOTAL_PRIZES
race_windows = []
LOG_FOLDER = './output'
RACE_WINDOW_LOG_FILE = f'{LOG_FOLDER}/race_window.txt'

"""
Rest the prize counter to 0.
"""
@app.route('/reset', methods=['GET'])
def reset():
    # Just to prevent a random request from resetting the prize
    if 'secret-key' not in request.headers:
        return "Secret key not found in request headers."
    
    experiment_id = request.headers.get('experiment-id')
    print(f"\nReceiving experiment {experiment_id}...\n")
    global num_prizes, race_windows
    with mutex:
        num_prizes = TOTAL_PRIZES
        with open(RACE_WINDOW_LOG_FILE, 'a') as file:
            for data in race_windows:
                file.write(f"{str(data)}\n")
        race_windows = []
        return "Prizes have been reset.\n"

"""
Expose the vulnerability by simulating some processing delay so
that the vulnerability is easier to be exploited.
"""
def log_transaction():
    # The larger the processing delay, the wider the race 
    # window, the 8 microseconds is somewhat arbitrary
    # time.sleep(PROCESSING_DELAY)
    # processing_delay()
    io_delay()

"""
Allow the winner to claim the prize if there is any left.
NOTE: This is a vulnerable endpoint with a type of race 
condition bugs known as TOCTOU (Time-of-Check to Time-of-Use).
"""
@app.route('/prize', methods=['GET'])
def prize():
    global num_prizes, race_windows
    request_id = request.headers.get('id')
    request_rcv_time = time.time()
    # Time of check (TOC in TOCTOU)
    if num_prizes > 0:
        start_time = time.time()
        log_transaction()
        # Time of use (TOU in TOCTOU)
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1e3
        race_windows.append(elapsed_time)

        num_prizes -= 1
        msg = f"ID {request_id} has claimed a prize. {num_prizes} left.\n"

        response = app.response_class(
            response=msg,
            status=200,
            headers={'end-time': str(request_rcv_time)}
        )
        return response
    else:
        msg = f"Request ID: {request_id} did not get the prize."
        response = app.response_class(
            response=msg,
            status=400,
            headers={'end-time': str(request_rcv_time)}
        )
        return response

if __name__ == '__main__':
    output_folder = LOG_FOLDER
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    app.run(debug=True, host=SERVER_IP, threaded=True, port=SERVER_PORT)
