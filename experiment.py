"""
experiment.py
----------------
by Mike Liao

Run the exploit code in many, many experiments.
"""

import os
import math
from datetime import datetime

USE_SCIPY = True
try:
    from scipy.stats import norm
except ImportError:
    USE_SCIPY = False

from arg_parser import parse_args, LatencyType
import exploit
from exploit import launch_attack, reset_counter, LEGIT_NUM_REQUESTS, compute_jitter_stats

RACE_WINDOW_MU = 1.5597
RACE_WINDOW_SIGMA = 1.4181
LOG_FOLDER = "./output"
log_file = None # Specify a log file in the main function

# Compute the analytical probability of success (assuming Normal RV's)
def compute_probability_of_success(race_window_mu, race_window_std_dev, jitter_mu, jitter_std_dev):
    joint_mu = jitter_mu - race_window_mu
    joint_std_dev = math.sqrt(race_window_std_dev ** 2 + jitter_std_dev ** 2)
    
    if USE_SCIPY:
        dist = norm(loc=joint_mu, scale=joint_std_dev)
        estimate = dist.cdf(0)
        return estimate
    else:
        return joint_mu, joint_std_dev

"""
Execute experiments with the given latency configuration.
"""
def main(num_experiments, verbose, latency_type: LatencyType, *latency_params):
    results = []
    jitter_ls = []
    num_unsuccessful_exploit = 0

    for i in range(num_experiments):
        if verbose:
            print(f"\nRunning experiment {i + 1}...\n")
        reset_counter(i + 1)  # Reset the counter at the beginning of each trial
        result = launch_attack(i + 1, log_file, verbose, latency_type, *latency_params)  # Pass trial index for logging
        results.append(result)

        legit_num_400 = exploit.CONCURRENT_REQUESTS - LEGIT_NUM_REQUESTS
        # Check if exactly 5 responses were 400, if so then the exploit was unsuccessful
        if result[1] == legit_num_400:
            num_unsuccessful_exploit += 1

    # Summary at the end of the experiment
    summary = f"\nExperiment Parameters:\n" \
        f"Number of iterations: {num_experiments}\n" \
        f"Number of requests per iteration: {exploit.CONCURRENT_REQUESTS}\n" \
        f"{latency_type}\n" \
        f"Latency parameters: {latency_params}\n"

    successful_exploits = num_experiments - num_unsuccessful_exploit
    success_rate = round(successful_exploits/num_experiments, 2)

    total_200 = sum(r[0] for r in results)
    total_400 = sum(r[1] for r in results)
    jitter_ls += [j for r in results for j in r[2]]
    total_successful_exploits = total_200 - num_experiments * LEGIT_NUM_REQUESTS
    avg_exploits_per_experiment = round(total_successful_exploits / successful_exploits, 2)

    local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    summary += f"\n------- Summary ({local_time}) -------\n"\
        f"Occurrences of successful exploits: {successful_exploits} (out of {num_experiments}, success rate: {success_rate})\n" \
        f"Average number of exploits per occurrence: {avg_exploits_per_experiment}\n" \
        f"\nTotal number of network requests: {num_experiments * exploit.CONCURRENT_REQUESTS}\n" \
        f"Total number of 200/400 responses: {total_200} / {total_400}\n" \
        f"Total number of successful exploits: {total_successful_exploits}\n"
    
    jitter_msg, jitter_mu, jitter_std_dev = compute_jitter_stats(jitter_ls)

    if USE_SCIPY:
        success_rate = compute_probability_of_success(RACE_WINDOW_MU,
            RACE_WINDOW_SIGMA, jitter_mu, jitter_std_dev)
        jitter_msg += f"\nAnalytical Success Rate: {success_rate:.4f}\n"
    else:
        joint_mu, joint_std_dev = compute_probability_of_success(RACE_WINDOW_MU,
            RACE_WINDOW_SIGMA, jitter_mu, jitter_std_dev)
        jitter_msg += f"\nJoint Distribution: N({joint_mu:.4f}, {joint_std_dev:.4f}^2)\n"

    log_file.write(summary)
    log_file.write(jitter_msg)
    jitter_log_file_name = f"{LOG_FOLDER}/jitter_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    jitter_log_file = open(jitter_log_file_name, "w")
    jitter_log_file.write(f"Jitter Values ({local_time})\n")
    for idx, jitter in enumerate(jitter_ls):
        jitter_log_file.write(f"{idx}: {jitter}\n")
    print(summary)
    print(jitter_msg)
    log_file.close()
    jitter_log_file.close()

if __name__ == "__main__":
    # Parse command line arguments
    latency_type, latency_params, num_experiments, verbose, num_concurrent_requests, server_ip = parse_args(True)

    # Create the output folder if it doesn't exist
    output_folder = LOG_FOLDER
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    log_file_name = f"{LOG_FOLDER}/{latency_type}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    log_file = open(log_file_name, "w")

    exploit.CONCURRENT_REQUESTS = num_concurrent_requests
    if server_ip:
        exploit.SERVER_IP = server_ip
        print("Connecting to server at", server_ip)

    # Run the test with the specified latency configuration
    main(num_experiments, verbose, latency_type, *latency_params)