#!/usr/bin/env python3

"""Preprocessor module."""

import glob
import logging
import re
import time
import uuid

import fire
from constants import TEX_DIR, PROJECT_DIR, EXPORTS_RDF_DOCUMENT_FILE
from rdflib import Graph, URIRef, Literal, Namespace
from scikg_adapter import (retrieve_env_snippets, retrieve_content_snippet,
                           retrieve_validated_exports)
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class Preprocessor:
    """
    RDFtex's preprocessor class.
    """

    def __init__(self) -> None:
        self.prefixes = {}
        self.exports = {}

    def __parse_rdftex_command(self, substring: str) -> list:
        """
        Parses the custom RDFtex commands and returns the parameters.
        """

        def resolve__prefix(string):
            """
            Replace parameters in prefix syntax by their full URIs
            """
            resolved = string

            for prefix, written_out in self.prefixes.items():
                if prefix + ":" in string:
                    resolved = string.replace(prefix + ":", written_out)

            return resolved

        param_list = []
        param_range = [0, 0]
        bracket_counter = 0

        index = 0

        for index, char in enumerate(substring):
            if char == "{":
                if not bracket_counter:
                    param_range[0] = index + 1
                bracket_counter += 1

            if char == "}":
                bracket_counter -= 1

                if not bracket_counter:
                    param_range[1] = index
                    param_list.append(substring[param_range[0]:param_range[1]])

                    param_range = [0, 0]
                    bracket_counter = 0

                    if substring[index + 1] != "{":
                        break

        resolved_param_list = [resolve__prefix(param) for param in param_list]

        return resolved_param_list, index + 1

    def __handle_prefix(self, line) -> None:
        """
        Handles lines with the custom \\rdfprefix command.
        """

        param_list, _ = self.__parse_rdftex_command(line)

        if len(param_list) != 2:
            logging.warning(
                f"RDFtex prefix commands require 2 parameters (got {len(param_list)}) -> Skipping prefix")
            return

        prefix, written_out, *_ = param_list

        self.prefixes[prefix] = written_out

    def __handle_import(self, processed_lines, imported_types, line, make_imports) -> None:
        """
        Handles lines with the custom \\rdfimport command.
        """

        if not make_imports:
            return
        
        param_list, _ = self.__parse_rdftex_command(line)

        if len(param_list) != 4:
            logging.warning(
                f"RDFtex import commands require 4 parameters (got {len(param_list)}) -> Skipping import")
            processed_lines.append(line)
            return

        label, citation_key, contribution_iri, skg, *_ = param_list

        try:
            content_snippet, contribution_type = retrieve_content_snippet(label, citation_key, contribution_iri, skg)
        except Exception as e:
            logging.warning(
                f"Skipping import due to error during snippet generation: {e}")
            return

        imported_types.add(contribution_type)
        processed_lines.append(content_snippet)

    def __handle_export(self, processed_lines, line, make_exports) -> None:
        """
        Handles lines with the custom \\rdfexport command.
        """

        if not make_exports:
            return

        param_list, _ = self.__parse_rdftex_command(line)

        if len(param_list) != 3:
            logging.warning(
                f"RDFtex export commands require 2 parameters (got {len(param_list)}) -> Skipping export")
            processed_lines.append(line)
            return

        export_name, export_type, other_pred_obj, *_ = param_list

        if export_name in self.exports:
            self.exports[export_name].append(
                ("https://example.org/scikg/terms/type", export_type))
        else:
            self.exports[export_name] = [
                ("https://example.org/scikg/terms/type", export_type)]

        if other_pred_obj:
            other_pred_obj_exports = [tuple(pred_obj.split(
                "=")) for pred_obj in other_pred_obj.split(",")]

            self.exports[export_name] += other_pred_obj_exports

    def __handle_property(self, processed_lines, line, make_exports) -> None:
        """
        Handles lines with the custom \\rdfproperty command.
        """

        processed_line = ""
        lastcommandendindex = 0
        parsing_successful = True

        for match in re.finditer(r"\\rdfproperty", line):

            commandstartindex = match.start()
            substring = line[commandstartindex:]

            param_list, commandlength = self.__parse_rdftex_command(substring)

            if len(param_list) != 3:
                logging.warning(
                    f"RDFtex property commands require 3 parameters (got {len(param_list)}) -> Skipping property")
                parsing_successful = False
                break

            export_name, export_predicate, export_object, *_ = param_list

            if make_exports:

                # FIXME This workaround is only necessary for the RDFtex papers and can be removed later
                # should be removable by adding a ~ in the .rdf.tex file
                if export_object == "<object>":
                    logging.warning(
                        f"Found <object> as export_object (RDFtex workaround) -> Skipping")
                    parsing_successful = False
                    break
            
                self.exports.setdefault(export_name, []).append((export_predicate, export_object))

            processed_line += line[lastcommandendindex:
                                   commandstartindex] + export_object
            lastcommandendindex = commandstartindex + commandlength

        if parsing_successful:
            processed_line += line[lastcommandendindex:]
            processed_lines.append(processed_line)
        else:
            processed_lines.append(line)

    def __preprocess_file(self, rdftexpath, imported_types, make_imports, make_exports) -> None:
        """
        Scans files for custom RDFtex commands and issues their processing.
        """

        preamble_end_index = -1
        processed_lines = []

        with open(rdftexpath, "r") as file:
            for linenumber, line in enumerate(file):
                if "\\begin{document}" in line:
                    # store preamble end index for insertion of custom environments if needed
                    preamble_end_index = len(processed_lines)

                if re.search(r"(?<! )\\rdfprefix", line):
                    logging.info(
                        f"Handling rdfprefix command in line {linenumber}...")

                    self.__handle_prefix(line)

                elif re.search(r"(?<! )\\rdfimport", line):
                    logging.info(
                        f"Handling rdfimport command in line {linenumber}...")

                    self.__handle_import(
                        processed_lines, imported_types, line, make_imports)

                elif re.search(r"(?<! )\\rdfexport", line):
                    logging.info(
                        f"Handling rdfexport command in line {linenumber}...")

                    self.__handle_export(processed_lines, line, make_exports)

                elif re.search(r"\\rdfproperty", line):
                    logging.info(
                        f"Handling rdfproperty command(s) in line {linenumber}...")

                    self.__handle_property(processed_lines, line, make_exports)

                else:
                    processed_lines.append(line)

        return preamble_end_index, processed_lines

    def run(self, make_imports=True, make_exports=True):
        """
        Issues the preprocessing on every .rdf.tex file found in the specified project directory.
        """
        
        start_time = time.time()

        imported_types = set()
        roottex_path = ""
        roottex_lines = []
        roottex_preamble_endindex = -1

        for rdftexpath in glob.glob(f"{TEX_DIR}{PROJECT_DIR}/*.rdf.tex"):
            logging.info(f"Preprocessing {rdftexpath}...")
            preamble_end_index, processed_lines = self.__preprocess_file(rdftexpath, imported_types, make_imports, make_exports)

            if preamble_end_index != -1:
                logging.info(f"Identified {rdftexpath} as root file...")
                roottex_path = rdftexpath.replace(".rdf.tex", ".tex")
                roottex_lines = processed_lines
                roottex_preamble_endindex = preamble_end_index
            else:
                texpath = rdftexpath.replace(".rdf.tex", ".tex")
                logging.info(f"Writing tex file at {texpath}...")

                with open(texpath, "w+") as file:
                    file.writelines(processed_lines)

        # add custom LaTeX environments to root file
        custom_envs = retrieve_env_snippets(imported_types, "MinSKG")
        for env in custom_envs.values():
            roottex_lines.insert(roottex_preamble_endindex, env)

        logging.info(f"Adding custom environments to {roottex_path}...")
        with open(roottex_path, "w+") as file:
            file.writelines(roottex_lines)

        # validate exports and generate/store exports RDF document
        validated_exports = retrieve_validated_exports(self.exports)
        
        exports_graph = Graph()
        terms = Namespace("https://example.org/scikg/terms/")
        publ = Namespace("https://example.org/scikg/publications/")

        publication_uri = publ[f"NEW/{uuid.uuid4().hex}"]
        new_publication = URIRef(publication_uri)
        export_ctr = 0

        for _, predicate_object_tuples in validated_exports.items():
            contrib_uri = URIRef(
                f"{publication_uri}/contrib{export_ctr}")

            exports_graph.add(
                (new_publication, terms["has_contribution"], contrib_uri))

            for pred, obj in predicate_object_tuples:
                exports_graph.add(
                    (contrib_uri, URIRef(pred), Literal(obj)))

            export_ctr += 1

        with open(f"{TEX_DIR}{PROJECT_DIR}{EXPORTS_RDF_DOCUMENT_FILE}", "w+") as file:
            file.write(exports_graph.serialize(format="ttl"))

        logging.info(
            f"{export_ctr} contribution(s) successfully exported to {TEX_DIR}{PROJECT_DIR}{EXPORTS_RDF_DOCUMENT_FILE}...")

        logging.info(f"Preprocessing took {time.time() - start_time} seconds!")

    def watch(self) -> None:
        """
        Issues the preprocessing if changes are made to the .rdf.tex files in the specified
        project directory. Note that this only works on Linux properly
        (s. https://william-yeh.net/post/2019/06/inotify-in-containers/).
        """

        def on_created(event):
            logging.info(
                f"{event.src_path} has been created -> Preprocessing...")
            self.run()
            logging.info(
                "=== Watching for updated .rdf.tex files. Use ctrl/C to stop ...")

        def on_modified(event):
            logging.info(
                f"{event.src_path} has been modified -> Preprocessing...")
            self.run()
            logging.info(
                "=== Watching for updated .rdf.tex files. Use ctrl/C to stop ...")

        def on_moved(event):
            logging.info(
                f"{event.src_path} moved to {event.dest_path} -> Preprocessing...")
            self.run()
            logging.info(
                "=== Watching for updated .rdf.tex files. Use ctrl/C to stop ...")

        event_handler = PatternMatchingEventHandler(
            patterns=["*.rdf.tex"],
            ignore_patterns=None,
            ignore_directories=True,
            case_sensitive=True)

        event_handler.on_created = on_created
        event_handler.on_modified = on_modified
        event_handler.on_moved = on_moved

        observer = Observer()
        observer.schedule(event_handler, TEX_DIR, recursive=True)

        logging.info(
            "=== Watching for updated .rdf.tex files. Use ctrl/C to stop ...")
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            observer.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    fire.Fire(Preprocessor().run)
