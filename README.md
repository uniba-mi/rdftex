
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

## !!! Attention !!!

If your are viewing the anonymized version of this repository, we want to make two important remarks:

- Some of the files included in the repository are not displayed correctly in the web interface of the anonymization service. If you encounter such a file, please download it for the best experience. Also some links within this README file do not work correctly.
- To get all files within the repository without downloading each file individually, we included a zipped archive of the repository called [rdftex.zip](./rdftex.zip) that you can easily download for your convenience.

## Summary

RDFtex is a framework that employs extended LaTeX documents and a preprocessor program to support the production of research publications that allow a bidirectional knowledge exchange with a scientific knowledge graph (SciKG). To implement the said knowledge exchange, RDFtex provides two main functionalities:
- The import functionality allows to import research contributions from a SciKG in LaTeX documents via custom import commands
- The export functionality allows to export original research contributions from LaTeX documents to a SciKG via custom export commands

This repository contains the prototypical implementation of RDFtex as proposed in the RDFtex paper and other sources.
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

The file [minskg.ttl](./src/minskg.ttl) contains the MinSKG serialized in the Turtle format.

## Usage

RDFtex operates on `.rdf.tex` files that feature custom commands for importing and exporting contributions. To preprocess `.rdf.tex` of a LaTeX project files and produce a PDF based on the automatically generated `.tex` files, there are several options.

Since Docker is employed, the only programs that have to be installed to run this project are:

- Docker
- Docker Compose

The [docker-compose.yml](./docker-compose.yml) is currently configured to run RDFtex on the exemplary `.rdf.tex` files in the [examples](./examples/) folder. If you want to run RDFtex on another LaTeX project, edit the `volumes` option therein accordingly. Another option is to copy your project to the [examples](./examples/) folder instead.

### Fully automatic build process (only on Linux hosts)

1. Run `docker-compose run rdftex-tex` to start up a `latexmk` instance that listens for changes made to `.tex` files in a command line.

2. Run `docker-compose run rdftex-watch` to start up a preprocessor instance that listens for changes made to `.rdf.tex` files in another command line.

3. Whenever you edit any `.rdf.tex` file and save, the preprocessor first generate the `.tex` files accordingly. `latexmk` will then detect the changes and thus recompile the PDF.

### Semi-automatic build process

1. Run `docker-compose run rdftex-tex` to start up a `latexmk` instance that listens for changes made to `.tex` files in a command line.

2. Run `docker-compose run rdftex` to start up a container for the preprocessor in another command line and attach to its command line.

3. Whenever you edit any `.rdf.tex` file and save, run `./preprocessor.py run` in the container command line to generate the `.tex` files. `latexmk` will then detect the changes and thus recompile the PDF.

## Examples

The [docker-compose.yml](./docker-compose.yml) is currently configured to run RDFtex on the exemplary `.rdf.tex` files in the [examples](./examples/) folder. To run RDFtex on the example files, proceed as described in section [Usage](#usage). For convenience, the folder already contains the `.tex` files generated by RDFtex as well as the resulting PDF and the RDF document containing the exported contributions.

The RDF document resulting from the preprocessing of the RDFtex paper can be found at [rdftex_paper_exports.ttl](./rdftex_paper_exports.ttl).

## License

See [LICENSE](./LICENSE)