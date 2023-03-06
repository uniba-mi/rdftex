#!/usr/bin/env python3
"""Benchmarking module."""

import glob
import logging
import os
import statistics
import subprocess
import time

import fire
import matplotlib.pyplot as plt
from rdflib import Graph

import scikg_adapter
from constants import MAIN_TEX_FILE, PROJECT_DIR, TEX_DIR


def runtime(runs=100):
    """
    Captures the runtime of RDFtex and Latexmk across n runs.
    Uses subprocess to avoid benefits from warmed up code across the runs since that
    would be unrealistic. Temporary LaTeX files and previously generated .tex files
    are removed in between runs, too.
    """

    configs = {
        "$R_{i,e} + L$": "python3 ./preprocessor.py run True True",
        "$R_{i} + L$": "python3 ./preprocessor.py run True False",
        "$R_{e} + L$": "python3 ./preprocessor.py run False True",
        "$L$": "",
    }

    results = {config: [] for config in configs}
    tmp_file_extensions = ["aux", "bbl", "blg", "fdb_latexmk", "fls", "log", "out", "xdv", "tex"] 

    for config, rdftex_command in configs.items():
        for ctr in range(runs):

            # remove temporary LaTeX files
            for extension in tmp_file_extensions:
                for path in glob.glob(f"{TEX_DIR}{PROJECT_DIR}/*.{extension}"):
                    if not ".rdf.tex" in path:
                        logging.info(f"Removing {path}...")
                        os.remove(path)

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

            # benchmark latexmk
            t2_start = time.perf_counter()
            subprocess.run([f"latexmk -pdf -xelatex -cd {TEX_DIR}{MAIN_TEX_FILE}"], capture_output=True, shell=True)
            t2_stop = time.perf_counter()
            latexmk_duration = t2_stop - t2_start

            results[config].append((rdftex_duration, latexmk_duration))
            logging.info(f"{config} - Run {ctr + 1} completed. RDFtex/Latexmk took {rdftex_duration}/{latexmk_duration} seconds.")

    # stacked bar chart of average runtimes
    average_latexmk = [statistics.mean([latexmk_time for _, latexmk_time in times]) for times in results.values()]
    average_rdftex = [statistics.mean([rdftex_time for rdftex_time, _ in times]) for times in results.values()]

    average_results = {
        "Latexmk": average_latexmk,
        "RDFtex": average_rdftex,
    }

    fig, ax = plt.subplots()
    bottom = [0 for _ in range(len(configs))]

    for which_average, average_result in average_results.items():
        color = "white" if which_average == "Latexmk" else "black"
        p = ax.bar(configs.keys(), average_result, label=which_average, color=color, edgecolor="black", bottom=bottom)
        bottom = [b + w for b, w in zip(bottom, average_result)]

    ax.set_ylabel("Seconds")
    ax.legend(loc="lower left")

    fig.savefig(f"benchmark-runtime-bar-{PROJECT_DIR.replace('/', '')}-{runs}.eps", bbox_inches="tight", format="eps")
    fig.savefig(f"benchmark-runtime-bar-{PROJECT_DIR.replace('/', '')}-{runs}.pdf", bbox_inches="tight")

    # box plot of runtimes
    aggregated_results = {scenario: [r + l for r, l in times] for scenario, times in results.items()}

    fig, ax = plt.subplots()
    boxplot = ax.boxplot(aggregated_results.values(), patch_artist=True, showfliers=False, medianprops={"color": "white"})
    ax.set_xticklabels(aggregated_results.keys())
    ax.set_ylabel("Seconds")

    for patch in boxplot["boxes"]:
        patch.set_facecolor("black")

    fig.savefig(f"benchmark-runtime-box-{PROJECT_DIR.replace('/', '')}-{runs}.eps", bbox_inches="tight", format="eps")
    fig.savefig(f"benchmark-runtime-box-{PROJECT_DIR.replace('/', '')}-{runs}.pdf", bbox_inches="tight")


def response_times(runs=1):

    query_response_times = {
        "MinSKG": {
            "https://example.org/scikg/publications/DBLP:conf/i-semantics/EhrlingerW16/contrib0": [],
            "https://example.org/scikg/publications/DBLP:conf/amia/NoyCFKTVM03/contrib0": [],
            "https://example.org/scikg/publications/DBLP:conf/emnlp/LuanHOH18/contrib0": [],
        },
        "ORKG": {
            "http://orkg.org/orkg/resource/R370883": [],
            "http://orkg.org/orkg/resource/R368042": [],
            "http://orkg.org/orkg/resource/R8199": [],
        } 
    }

    # query minskg
    for ctr_one, entity in enumerate(query_response_times["MinSKG"].keys()):
        for ctr_two in range(runs):
            t1_start = time.perf_counter()
            result = scikg_adapter.get_tree_for_contribution_entity(entity, "MinSKG")
            t1_stop = time.perf_counter()
            response_time = t1_stop - t1_start

            g = Graph()
            g.parse(data=result.text)

            query_response_times["MinSKG"][entity].append((len(g), response_time))
            logging.info(f"Querying entity {ctr_one + 1} - Run {ctr_two + 1} from MinSKG took {response_time} seconds.")

    # query orkg
    for ctr_one, entity in enumerate(query_response_times["ORKG"].keys()):
        for ctr_two in range(runs):
            t1_start = time.perf_counter()
            result = scikg_adapter.get_tree_for_contribution_entity(entity, "ORKG")
            t1_stop = time.perf_counter()
            response_time = t1_stop - t1_start

            g = Graph()
            g.parse(data=result.text)

            query_response_times["ORKG"][entity].append((len(g), response_time))
            logging.info(f"Querying entity {ctr_one + 1} - Run {ctr_two + 1} from ORKG took {response_time} seconds.")
            time.sleep(3)

    print(query_response_times)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fire.Fire()
