"""
arg_parser.py
----------------
by Mike Liao

Parses command line arguments for the experiment configuration.
"""

import argparse
import ast
from enum import Enum

NUM_EXPERIMENTS = 100

"""
Enum for the type of network latency to simulate
"""
class LatencyType(Enum):
    NONE = 1
    CONSISTENT = 2
    JITTER = 3
    JITTER_NORMAL = 4

def parse_args(multiple_experiments = False):
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Network Latency Configuration')
    parser.add_argument('-i', '--ip', type=str, help='IP address of the server')
    parser.add_argument('-c', '--concurrent', type=int, help='Number of concurrent requests')
    parser.add_argument('-s', '--silent', action='store_true', help='Run silently without printing output')
    parser.add_argument('-d', '--delay', type=float, help='Simulate consistent network latency')
    parser.add_argument('-j', '--jitter', type=float, help='Simulate network jitter')
    parser.add_argument('-jn', '--jitter_norm_dist', type=str, help='Simulate network jitter with a normal distribution')
    
    if multiple_experiments:
        parser.add_argument('-n', '--num_experiments', type=int, default=NUM_EXPERIMENTS, help='Number of experiments to run')
    
    args = parser.parse_args()
    num_experiments = args.num_experiments if multiple_experiments else 0
    verbose = not args.silent
    number_of_concurrent_requests = args.concurrent if args.concurrent else 2
    latency_type = LatencyType.NONE
    latency_params = ()
    server_ip = args.ip if args.ip else None

    type_flags = 0
    if args.delay:
        type_flags += 1
    if args.jitter:
        type_flags += 1
    if args.jitter_norm_dist:
        type_flags += 1

    if type_flags > 1:
        raise ValueError("Only specify one type of latency at an experiment")
    
    if args.delay:
        delay = float(args.delay / 1000)  # Convert to seconds
        latency_type = LatencyType.CONSISTENT
        latency_params = (delay,)  # Add args.delay to latency_params
    if args.jitter:
        latency_type = LatencyType.JITTER
        mean_latency = float(args.jitter / 1000)  # Convert to seconds
        latency_params = (mean_latency,)
    if args.jitter_norm_dist:
        latency_type = LatencyType.JITTER_NORMAL
        jitter_norm_dist = ast.literal_eval(args.jitter_norm_dist)
        mean_latency, std_dev = jitter_norm_dist
        mean_latency = float(mean_latency / 1000)
        std_dev = float(std_dev / 1000)
        latency_params = (mean_latency, std_dev)

    return latency_type, latency_params, num_experiments, verbose, number_of_concurrent_requests, server_ip