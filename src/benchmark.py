#!/usr/bin/env python3
"""Benchmarking module."""

import logging
import subprocess
import time
import matplotlib.pyplot as plt
import time

import fire


def run(runs=100):
    """
    Captures the runtime of the preprocessing across n runs.
    Uses subprocess to avoid benefits from warmed up code across the runs since that
    would be unrealistic.
    """

    scenarios = {
        "imports only": "python3 ./preprocessor.py run True False",
        "exports only": "python3 ./preprocessor.py run False True",
        "imports and exports": "python3 ./preprocessor.py run True True",
    }

    results = {key: [] for key in scenarios}

    # benchmark rdftex
    for scenario, rdftex_command in scenarios.items():
        for ctr in range(runs):
            t1_start = time.perf_counter()
            subprocess.run([rdftex_command], capture_output=True, shell=True)
            t1_stop = time.perf_counter()
            rdftex_duration = t1_stop - t1_start

            results[scenario].append(rdftex_duration)

            logging.info(f"{scenario} - Run {ctr + 1} completed. RDFtex took {rdftex_duration} seconds.")

    # # initial cleanup
    # subprocess.run(["latexmk -c -cd ../tex/example.tex"], capture_output=True, shell=True)

    # # benchmark latexmk
    # t2_start = time.perf_counter()
    # subprocess.run(["latexmk -pdf -xelatex -cd ../tex/example.tex"], capture_output=True, shell=True)
    # t2_stop = time.perf_counter()
    # latexmk_duration = t2_stop - t2_start

    fig, ax = plt.subplots()
    boxplot = ax.boxplot(results.values(), patch_artist=True, showfliers=False, medianprops={"color": "white"})
    ax.set_xticklabels(results.keys())
    ax.set_ylabel("Seconds")
    ax.set_title(f"RDFtex Runtime")

    for patch in boxplot["boxes"]:
        patch.set_facecolor("black")

    fig.savefig("benchmark-runtime-boxplot.pdf", bbox_inches="tight")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fire.Fire(run)
