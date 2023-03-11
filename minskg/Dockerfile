FROM ubuntu:23.04

RUN apt-get update && apt-get install --yes python3.11
RUN apt-get update && apt-get install --yes python3-pip

RUN pip install -U rdflib
RUN pip install -U bibtexparser
RUN pip install -U pylatexenc
RUN pip install -U flask

VOLUME [ "/src" ]
WORKDIR /src

ENTRYPOINT bash