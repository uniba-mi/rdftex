#!/usr/bin/env python3
"""Benchmarking module."""

import logging
import subprocess
import time
import matplotlib.pyplot as plt

import fire


def run(runs=10):
    """
    Captures the runtime of the preprocessing across n runs.
    Uses subprocess to avoid benefits from warmed up code across the runs since that
    would be unrealistic.
    """

    rdftex_times = []
    latexmk_times = []

    rdftex_command = "python3 ./preprocessor.py run"
    latexmk_command = "latexmk -pdf -xelatex -cd ../tex/example.tex"

    for ctr in range(runs):
        # initial cleanup
        subprocess.run(["latexmk -c -cd ../tex/example.tex"], capture_output=False, shell=True, check=False)

        # benchmark rdftex imports and exports
        t1_start = time.perf_counter()
        subprocess.run([rdftex_command], capture_output=True, shell=True, check=False)
        t1_stop = time.perf_counter()
        rdftex_duration = t1_stop - t1_start
        rdftex_times.append(rdftex_duration)

        # benchmark latexmk
        t2_start = time.perf_counter()
        subprocess.run([latexmk_command], capture_output=True, shell=True, check=False)
        t2_stop = time.perf_counter()
        latexmk_duration = t2_stop - t2_start
        latexmk_times.append(latexmk_duration)

        logging.info(f"Run {ctr} completed. RDFtex took {rdftex_duration} seconds. latexmk took {latexmk_duration} seconds.")

    logging.info(f"Longest run: {max(rdftex_times)}")
    logging.info(f"Fastest run: {min(rdftex_times)}")
    logging.info(f"Average time per run: {sum(rdftex_times) / runs}")

    fig, ax = plt.subplots()
    VP = ax.boxplot([rdftex_times, latexmk_times], positions=[2, 4], widths=1.5, patch_artist=True,
                    showmeans=False, showfliers=False,
                    medianprops={"color": "white", "linewidth": 0.5},
                    boxprops={"facecolor": "C0", "edgecolor": "white",
                              "linewidth": 0.5},
                    whiskerprops={"color": "C0", "linewidth": 1.5},
                    capprops={"color": "C0", "linewidth": 1.5})

    # ax.set(xlim=(0, 8), xticks=np.arange(1, 8),
    #        ylim=(0, 8), yticks=np.arange(1, 8))

    fig.savefig("benchmark-boxplot.pdf")

    # plt.show()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fire.Fire(run)
