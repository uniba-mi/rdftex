#!/usr/bin/env python3
"""Benchmarking module."""

import logging
import subprocess
import time
import matplotlib.pyplot as plt
import time
import os
import statistics

import fire


def run(runs=10):
    """
    Captures the runtime of RDFtex and Latexmk across n runs.
    Uses subprocess to avoid benefits from warmed up code across the runs since that
    would be unrealistic. Temporary LaTeX files are removed in between runs, too.
    """

    scenarios = {
        "$R_{i,e} + L$": "python3 ./preprocessor.py run True True",
        "$R_{i} + L$": "python3 ./preprocessor.py run True False",
        "$R_{e} + L$": "python3 ./preprocessor.py run False True",
        "$L$": "",
    }

    results = {scenario: [] for scenario in scenarios}

    for scenario, rdftex_command in scenarios.items():
        for ctr in range(runs):
            # initial cleanup
            if os.path.isfile("/tex/example.aux"):
                os.remove("/tex/example.aux")

            if os.path.isfile("/tex/example.bbl"):
                os.remove("/tex/example.bbl")

            if os.path.isfile("/tex/example.blg"):
                os.remove("/tex/example.blg")

            if os.path.isfile("/tex/example.fdb_latexmk"):
                os.remove("/tex/example.fdb_latexmk")

            if os.path.isfile("/tex/example.fls"):
                os.remove("/tex/example.fls")

            if os.path.isfile("/tex/example.log"):
                os.remove("/tex/example.log")

            if os.path.isfile("/tex/example.out"):
                os.remove("/tex/example.out")
                
            # benchmark rdftex
            if rdftex_command:
                t1_start = time.perf_counter()
                subprocess.run([rdftex_command], capture_output=True, shell=True)
                t1_stop = time.perf_counter()
                rdftex_duration = t1_stop - t1_start
            else:
                # this has to be run to make tex compilable
                subprocess.run(["python3 ./preprocessor.py run False False"], capture_output=True, shell=True)
                rdftex_duration = 0

            logging.info(f"{scenario} - Run {ctr + 1} completed. RDFtex took {rdftex_duration} seconds.")

            # benchmark latexmk
            t2_start = time.perf_counter()
            subprocess.run(["latexmk -pdf -xelatex -cd ../tex/example.tex"], capture_output=False, shell=True)
            t2_stop = time.perf_counter()
            latexmk_duration = t2_stop - t2_start

            results[scenario].append((rdftex_duration, latexmk_duration))

    # stacked bar chart of average runtimes
    average_latexmk = [statistics.mean([latexmk_time for _, latexmk_time in times]) for scenario, times in results.items()]
    average_rdftex = [statistics.mean([rdftex_time for rdftex_time, _ in times]) for scenario, times in results.items()]

    weight_counts = {
        "Latexmk": average_latexmk,
        "RDFtex": average_rdftex,
    }

    fig, ax = plt.subplots()
    bottom = [0 for _ in range(len(scenarios))]

    for boolean, weight_count in weight_counts.items():
        print(scenarios.keys(), bottom)
        p = ax.bar(scenarios.keys(), weight_count, label=boolean, bottom=bottom)
        bottom = [b + w for b, w in zip(bottom, weight_count)]

    ax.set_ylabel("Seconds")
    ax.set_title("RDFtex + Latexmk Runtime (n = 100)")
    ax.legend(loc="upper right")

    fig.savefig("benchmark-runtime-bar.pdf", bbox_inches="tight")

    # box plot of runtimes
    aggregated_results = {scenario: [r + l for r, l in times] for scenario, times in results.items()}

    fig, ax = plt.subplots()
    boxplot = ax.boxplot(aggregated_results.values(), patch_artist=True, showfliers=False, medianprops={"color": "white"})
    ax.set_xticklabels(aggregated_results.keys())
    ax.set_ylabel("Seconds")
    ax.set_title(f"RDFtex Runtime + Latexmk Runtime (n = 100)")

    for patch in boxplot["boxes"]:
        patch.set_facecolor("black")

    fig.savefig("benchmark-runtime-box.pdf", bbox_inches="tight")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fire.Fire(run)
