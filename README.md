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

RDFtex is a framework that employs extended LaTeX documents and a preprocessor program to support the production of research publications that allow a bidirectional knowledge exchange with a scientific knowledge graph (SciKG). To implement the said knowledge exchange, RDFtex provides two main functionalities:

- The import functionality allows to import research contributions from a SciKG in LaTeX documents via custom import commands
- The export functionality allows to export original research contributions from LaTeX documents to a SciKG via custom export commands

This repository contains the proof-of-concept implementation of RDFtex and other sources as proposed in the RDFtex papers (https://link.springer.com/chapter/10.1007/978-3-031-16802-4_3).

## MinSKG

Currently, RDFtex can only interact with the MinSKG, a minimal SciKG that serves as a temporal makeshift for an actual SciKG. The MinSKG is populated with all publications that are used as references for the RDFtex paper. The contextual information of the publications, i.e., the metadata, was added automatically by parsing their entries from the `bibtex` file using a simple script. The contentual information, i.e, their contributions, was added manually.

There are currently five types of contributions that can be imported from and exported to the MinSKG. Each of them are represented using type-specific properties in the MinSKG. The following list specifies the supported contributions and their properties (as URIs):

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

RDFtex operates on `.rdf.tex` files that feature custom commands for importing and exporting contributions. To preprocess `.rdf.tex` of a LaTeX project files and produce a PDF based on the automatically generated `.tex` files, there are several options.

### Installation

The recommended and easier way to run RDFtex is to use Docker, which also ensures reproducibility. In this case, you only have to install:

- Docker
- Docker Compose

The [docker-compose.yml](./docker-compose.yml) is currently configured to run RDFtex on the exemplary `.rdf.tex` files in the [tex](./tex/) folder. If you want to run RDFtex on another LaTeX project, edit the `volumes` option therein accordingly. Another option is to copy your project to the [tex](./tex/) folder instead.

Running the software without Docker might cause problems depending on the host system. If you still want to execute the software without Docker you have to install:

- Python 3.9
- The Python dependencies listed in [requirements.txt](./src/requirements.txt)
- [Latexmk](https://mg.readthedocs.io/latexmk.html)

### Fully automatic build process (only on Linux hosts)

1. Run `docker-compose run latexmk` in a command line to start up a `latexmk` container that listens for changes made to `.tex` files.

2. Run `docker-compose run rdftex-watch` in another command line to start up a preprocessor container that listens for changes made to `.rdf.tex` files. `latexmk` will then detect the changes and thus recompile the PDF.

3. Whenever you edit any `.rdf.tex` file and save, the preprocessor first generate the `.tex` files accordingly. `latexmk` will then detect the changes and thus recompile the PDF.

### Semi-automatic build process

1. Run `docker-compose run latexmk` in a command line to start up a `latexmk` container that listens for changes made to `.tex` files.

2. Run `docker-compose run rdftex` in another command line to start up a container for the preprocessor and attach to its command line.

3. Whenever you edit any `.rdf.tex` file and save, run `python3 preprocessor.py run` in the container command line to trigger the preprocessor and generate the `.tex` files.

To run the benchmark used in the paper to assess the duration of the preprocessing on **your** RDFtex project, run `python3 benchmark.py` after steps 1 and 2 of the semi-automatic build process.

### Semi-automatic build process (without Docker)

1. Run `latexmk -pvc -pdf -xelatex -cd /tex/example.tex` in a command line to listen for changes made to `.tex` files.

2. Open another command line and move to the [src](./src/) folder.

3. Whenever you edit any `.rdf.tex` file and save, run `python3 preprocessor.py run` in the new command line to trigger the preprocessor and generate the `.tex` files.

## Examples

The [docker-compose.yml](./docker-compose.yml) is currently configured to run RDFtex on the exemplary `.rdf.tex` files in the [tex](./tex/) folder. To run RDFtex on the example files, proceed as described in section [Usage](#usage). For convenience, the repository already contains the `.tex` files generated by RDFtex as well as the resulting PDF and the RDF export document. The examples use the [LNCS LaTeX template](https://www.springer.com/gp/computer-science/lncs/conference-proceedings-guidelines) to showcase RDFtex's compatibility with popular templates.

The RDF document resulting from the preprocessing of the RDFtex paper can be found at [rdftex_paper_exports.ttl](./rdftex_paper_exports.ttl).

## License

See [LICENSE](./LICENSE)
