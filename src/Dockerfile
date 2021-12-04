FROM ubuntu:20.04

RUN apt-get update && apt-get install --yes python3.9
RUN apt-get update && apt-get install --yes python3-pip
RUN apt-get update && apt-get install --yes pylint

RUN pip install -U rdflib
RUN pip install -U bibtexparser
RUN pip install -U pylatexenc
RUN pip install -U watchdog
RUN pip install -U fire
RUN pip install -U pyparsing

VOLUME [ "/src" ]
WORKDIR /src

ENTRYPOINT bash