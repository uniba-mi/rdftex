#!/usr/bin/env python3
"""Benchmarking module."""

import logging
import subprocess
import time

import fire


def run(runs=100):
    """
    Benchmarks the runtime of the preprocessing across n runs.
    Uses subprocess to avoid benefits from warmed up code across the runs since that
    would be unrealistic.
    """

    times_per_run = []

    command = "./preprocessor.py run"

    for ctr in range(runs):
        t1_start = time.perf_counter()
        subprocess.run([command], capture_output=True, shell=True, check=False)
        t1_stop = time.perf_counter()

        logging.info(f"Run {ctr} completed..")
        times_per_run.append(t1_stop - t1_start)

    logging.info(f"Longest run: {max(times_per_run)}")
    logging.info(f"Fastest run: {min(times_per_run)}")
    logging.info(f"Average time per run: {sum(times_per_run) / runs}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fire.Fire(run)
