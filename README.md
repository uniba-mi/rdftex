<p align="center">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="license">
    <br>
</p>
    
<h2 align="center">RDFtex: Knowledge Exchange between LaTeX-based Research Publications and SciKGs</h2>

<p align="center">
    <a href="#summary">Summary</a>
    •
    <a href="#minskg">MinSKG</a>
    •
    <a href="#usage">Usage</a>
    •
    <a href="#examples">Examples</a>
    •
    <a href="#license">License</a>
</p>

## Summary

RDFtex is a framework that employs custom LaTeX commands and a preprocessor program to implement a bidirectional knowledge exchange with scientific knowledge graphs (SciKGs). To implement the said knowledge exchange, RDFtex provides two main functionalities:

- The import functionality allows to import research contributions from a specified SciKG in LaTeX documents via custom import commands.
- The export functionality allows to export original research contributions from LaTeX documents to a SciKG via custom export commands.

This repository contains the proof-of-concept implementation of RDFtex and other sources as proposed in our [TPDL 2022 RDFtex paper](https://link.springer.com/chapter/10.1007/978-3-031-16802-4_3) and its extended version currently in preparation.

## MinSKG

Currently, RDFtex can only interact with the MinSKG, a minimal SciKG that serves as a makeshift for an actual SciKG. The MinSKG is populated with all publications that are used as references for the RDFtex paper. The contextual information of the publications, i.e., the metadata, was added automatically by parsing their entries from the `bibtex` file using a simple script. The contentual information, i.e, their contributions, was added manually.

The MinSKG supports five types of contributions for importing and exporting. Each of them are represented using type-specific properties. The following list specifies the supported contributions and their properties (as IRIs):

- Definitions
  - `https://example.org/scikg/terms/type`
  - `https://example.org/scikg/terms/definition_content`
- Datasets
  - `https://example.org/scikg/terms/type`
  - `https://example.org/scikg/terms/dataset_name`
  - `https://example.org/scikg/terms/dataset_description`
  - `https://example.org/scikg/terms/dataset_domain`
  - `https://example.org/scikg/terms/dataset_url`
- Figures
  - `https://example.org/scikg/terms/type`
  - `https://example.org/scikg/terms/figure_description`
  - `https://example.org/scikg/terms/figure_url`
  - `https://example.org/scikg/terms/figure_mime`
- Simple experimental results
  - `https://example.org/scikg/terms/type`
  - `https://example.org/scikg/terms/expresult_description`
  - `https://example.org/scikg/terms/expresult_result`
  - `https://example.org/scikg/terms/expresult_samplesize`
- Software
  - `https://example.org/scikg/terms/type`
  - `https://example.org/scikg/terms/software_name`
  - `https://example.org/scikg/terms/software_description`
  - `https://example.org/scikg/terms/software_url`

The file [minskg.ttl](./src/minskg.ttl) contains the MinSKG, as employed for the preparation of the research paper, serialized in the Turtle format.

## Usage

RDFtex operates on `.rdf.tex` files that allow the usage of the custom RDFtex commands for importing and exporting contributions. To preprocess the `.rdf.tex` files of a LaTeX project files and produce a PDF based on the automatically generated `.tex` files, there are several options.

### Setup

The recommended and easiest way to run RDFtex is to use Docker, which also ensures reproducibility. In this case, you only have to install:

- Docker
- Docker Compose

Out of the box, RDFtex is configured to run RDFtex on the exemplary `.rdf.tex` files in the [example-basic folder](./tex/example-basic/). If you want to start a new LaTeX project that employs RDFtex, create a new folder in the [tex](./tex/) folder and adjust the constants in the [constants.py file](./src/constants.py) accordingly.

If you want to run RDFtex on an existing LaTeX project, move your LaTeX project folder into the [tex](./tex/) folder and adjust the constants in the [constants.py file](./src/constants.py) file accordingly. Then, create copies of each `.tex` file in the folder with the `.rdf.tex` file extension.

Running the software without Docker might cause problems depending on the host system. If you still want to execute the software without Docker you have to install:

- Python 3.11
- The Python dependencies listed in [requirements.txt](./src/requirements.txt)
- [Latexmk](https://mg.readthedocs.io/latexmk.html)

### Fully automatic build process (only on Linux hosts)

1. Run `docker compose run latexmk` in a command line to start up a `latexmk` container that listens for changes made to `.tex` files.

2. Run `docker compose run --service-ports minskg` in another command line to the MinSKG server.

3. Run `docker compose run rdftex-watch` in another command line to start up a preprocessor container that listens for changes made to `.rdf.tex` files. `latexmk` will then detect the changes and thus recompile the PDF.

4. Whenever you edit and save any `.rdf.tex` file, the preprocessor first generate the `.tex` files. `latexmk` will then detect the changes and thus recompile the PDF.

### Semi-automatic build process

1. Run `docker-compose run latexmk` in a command line to start up a `latexmk` container that listens for changes made to `.tex` files.

2. Run `docker compose run --service-ports minskg` in another command line to the MinSKG server.

3. Run `docker-compose run rdftex` in another command line to start up a container for the preprocessor and attach to its command line.

4. Whenever you edit any `.rdf.tex` file and save, run `python3 preprocessor.py` in the container command line to trigger the preprocessor and generate the `.tex` files.

### Semi-automatic build process (without Docker)

1. Run `latexmk -pvc -pdf -xelatex -cd /tex/example.tex` in a command line to listen for changes made to `.tex` files.

2. Open another command line and navigate to the [src](./src/) folder.

3. Whenever you edit any `.rdf.tex` file and save, run `python3 preprocessor.py` in the new command line to trigger the preprocessor and generate the `.tex` files.

### Benchmarks

⚠ Attention ⚠: Rerunning the benchmarks might overwrite the plots in the [benchmark-results folder](./src/benchmark-results/).

To run the benchmark used in the paper to assess the runtime of the preprocessing on the LaTeX project specified in the [constants.py file](./src/constants.py), run `python3 benchmark.py runtime` or `python3 benchmark.py response_times` after steps 1 and 2 of the semi-automatic build process. The plots showing the benchmark results, can be found in the [benchmark-results folder](./src/benchmark-results/).

The contribution entities used to assess the query response times of the MinSKG SPARQL interface and the [ORKG](https://orkg.org) SPARQL interface can be found in the [benchmark.py file](./src/benchmark.py).

## Examples

The [tex](./tex/) folder contains two example projects that employ RDFtex:

- [example-basic](./tex/example-basic/): A project with one import and export for each supported contribution type, which totals five imports and five exports.
- [example-many](./tex/example-many/): A derivation of the example-basic project, where each import and export is included 20 times, resulting in 100 imports and 100 exports. Use this project only for benchmarking.

The examples use the [LNCS LaTeX template](https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines) to showcase RDFtex's compatibility with typical LaTeX publication templates.

## Exports RDF Documents of RDFtex papers

The exports RDF document resulting from the preprocessing of the TPDL 2022 RDFtex paper can be found [here](./exports_tpdl22_rdftex_paper.ttl).

The exports RDF document resulting from the preprocessing of the extended RDFtex paper currently in preparation can be found at [here](./exports_extended_rdftex_paper.ttl).

## License

See [LICENSE](./LICENSE)
