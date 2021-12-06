#!/usr/bin/env python3

"""Preprocessor module."""

import glob
import logging
import re
import time
from configparser import ConfigParser

import fire
from pyparsing import ParseException
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

from minskg import MinSKG
from utils import add_custom_envs, generate_snippet


class Preprocessor:
    """
    RDFtex's preprocessor class.
    """

    def __init__(self) -> None:
        self.config = ConfigParser()
        self.config.read("config.ini")

        self.texdir = self.config["main"]["texdir"]
        self.exportpath = self.config["main"]["exportpath"]

        if self.config["main"]["skg"] == "MinSKG":
            self.skg = MinSKG()
        else:
            raise NotImplementedError(
                "Currently, only the MinSKG is supported!")

        self.vocab = {}
        self.exports = {}

    def __parse_rdftex_command(self, substring: str) -> list:
        """
        Parses the custom RDFtex commands and returns the parameters.
        """

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

        # replace prefxes by full URIs
        processed_param_list = []

        for param in param_list:
            resolvedparam = self.__resolve__prefix(param)
            processed_param_list.append(resolvedparam)

        return processed_param_list, index + 1

    def __resolve__prefix(self, string):
        resolved = string

        for prefix, written_out in self.vocab.items():
            if prefix + ":" in string:
                resolved = string.replace(prefix + ":", written_out)

        return resolved

    def __handle_prefix(self, line) -> None:
        """
        Handles the custom \\rdfprefix command.
        """

        param_list, _ = self.__parse_rdftex_command(line)

        if len(param_list) != 2:
            logging.warning(
                f"RDFtex prefix commands require 2 parameters (got {len(param_list)}) -> Skipping")
            return

        prefix, written_out, *_ = param_list

        self.vocab[prefix] = written_out

    def __handle_import(self, processed_lines, imported_types, line) -> None:
        """
        Handles the custom \\rdfimport command.
        """

        param_list, _ = self.__parse_rdftex_command(line)

        if len(param_list) != 3:
            logging.warning(
                f"RDFtex import commands require 3 parameters (got {len(param_list)}) -> Skipping import")
            processed_lines.append(line)
            return

        import_label, citation_key, import_uri, *_ = param_list

        try:
            contribution_data = self.skg.query(
                f"SELECT ?p ?o WHERE {{<{import_uri}> ?p ?o .}}")
            contribution_data = {str(entry[0]): str(
                entry[1]) for entry in contribution_data}
            print(import_uri)
        except ParseException:
            logging.warning(
                "Error during processing SPARQL query -> Skipping import")
            processed_lines.append(line)
            return

        import_type = contribution_data["https://example.org/scikg/terms/type"]
        imported_types.add(import_type)

        snippet = generate_snippet(
            contribution_data, import_label, citation_key)
        processed_lines.append(snippet)

    def __handle_export(self, processed_lines, line) -> None:
        """
        Handles the custom \\rdfexport command.
        """

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

    def __handle_property(self, processed_lines, line) -> None:
        """
        Handles the custom \\rdfproperty command.
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

            # This workaround is only necessary for the RDFtex paper and can be removed later
            if export_object == "<object>":
                logging.warning(
                    f"Found <object> as export_object (rdftex workaround) -> Skipping")
                parsing_successful = False
                break

            if export_name in self.exports:
                self.exports[export_name].append(
                    (export_predicate, export_object))
            else:
                self.exports[export_name] = [
                    (export_predicate, export_object)]

            processed_line += line[lastcommandendindex:
                                   commandstartindex] + export_object
            lastcommandendindex = commandstartindex + commandlength

        if parsing_successful:
            processed_line += line[lastcommandendindex:]
            processed_lines.append(processed_line)
        else:
            processed_lines.append(line)

    def __preprocess_file(self, rdftexpath, imported_types) -> None:
        """
        Scans files for custom RDFtex commands and issues their processing.
        """

        preamble_end_index = -1
        processed_lines = []

        with open(rdftexpath, "r") as file:
            for linenumber, line in enumerate(file):
                if "\\begin{document}" in line:
                    # store preamble end index for potential insertion of custom environments
                    preamble_end_index = len(processed_lines)

                if re.search(r"(?<! )\\rdfprefix", line):
                    logging.info(
                        f"Handling rdf vocab command in line {linenumber}...")

                    self.__handle_prefix(line)

                elif re.search(r"(?<! )\\rdfimport", line):
                    logging.info(
                        f"Handling rdf import command in line {linenumber}...")

                    self.__handle_import(
                        processed_lines, imported_types, line)

                elif re.search(r"(?<! )\\rdfexport", line):
                    logging.info(
                        f"Handling rdf export command in line {linenumber}...")

                    self.__handle_export(processed_lines, line)

                elif re.search(r"\\rdfproperty", line):
                    logging.info(
                        f"Handling rdf property command(s) in line {linenumber}...")

                    self.__handle_property(processed_lines, line)

                else:
                    processed_lines.append(line)

        return preamble_end_index, processed_lines

    def run(self):
        """
        Issues the preprocessing on every .rdf.tex file found in the specified project directory.
        """

        imported_types = set()
        root_tex_path = ""
        root_tex_lines = []
        root_tex_preamble_end_index = -1

        for rdftexpath in glob.glob(f"{self.texdir}*.rdf.tex"):
            logging.info(f"Preprocessing {rdftexpath}...")
            preamble_end_index, processed_lines = self.__preprocess_file(rdftexpath, imported_types)

            if preamble_end_index != -1:
                logging.info(f"Identified {rdftexpath} as root file...")
                root_tex_path = rdftexpath.replace(".rdf.tex", ".tex")
                root_tex_lines = processed_lines
                root_tex_preamble_end_index = preamble_end_index
            else:
                texpath = rdftexpath.replace(".rdf.tex", ".tex")
                logging.info(f"Writing tex file at {texpath}...")

                with open(texpath, "w+") as file:
                    file.writelines(processed_lines)

        add_custom_envs(root_tex_lines, root_tex_preamble_end_index, imported_types)

        logging.info(f"Adding custom environments to {root_tex_path}...")
        with open(root_tex_path, "w+") as file:
            file.writelines(root_tex_lines)

        self.skg.generate_exports_kg(self.exports, self.exportpath)

    def watch(self) -> None:
        """
        Issues the preprocessing when there changes made to the .rdf.tex files in the specified
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
        observer.schedule(event_handler, self.texdir, recursive=True)

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
    fire.Fire(Preprocessor)
