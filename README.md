# CS109 Challenge - Race to the Race Condition

## Introduction

This is the repository for my 2024 Winter Quarter CS109 Challenge project. This repo contains the server / client code, collected reports that are referenced in the written paper, and the jupyter notebooks used to compute the reported stats.

## Testing the Project

Here is the sample script to set up the server for testing. The scripts below assume OS to be either MacOS or Linux. For Windows, the steps are similar but the specific commands are slightly different (not shown here).

- Server side: the server runs on `Flask` so it has to be installed.

```python
# Create a new virtual environment
python3 -m venv .venv

# Activate the VM and install the required packages
source .venv/bin/activate
pip3 install -r requirement.txt

# Starts the server
python3 buggy_server.py
```

- Client side: there is no hard dependency but if `scipy` is installed, there is code to compute stats using `scipy`. If installation is not possible in the client machine, the code should still run.

```python
# Run a single hack
python3 exploit.py -i [ip of the server]

# Run 200 (configurable) hacks for testing
python3 experiment.py -i [ip of the server]
```

## Configurations

The client code can be invoked with various different arguments to simulate the hack under different configurations. For example, to run the hacks with more than 2 requests, use `-c 10` to hack using 10 requests. To run the experiments for 600 times, use `-n 600`. For a full argument list, check out [arg_parser.py](./arg_parser.py)
