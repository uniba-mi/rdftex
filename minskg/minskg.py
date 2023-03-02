"""MinSKG module."""

import logging
import re
import uuid

import bibtexparser
from bibtexparser.bparser import BibTexParser
from pylatexenc.latex2text import LatexNodes2Text
from rdflib import Graph, Literal, Namespace, URIRef

class MinSKG():
    """
    The class representing the MinSKG that is used to demonstrate RDFtex.
    """

    def __init__(self) -> None:
        self.skg = Graph().parse("./minskg.ttl")
        self.terms = Namespace("https://example.org/scikg/terms/")
        self.publ = Namespace("https://example.org/scikg/publications/")
        self.supported_contributions = self.__get_supported_contributions()

        logging.basicConfig(level=logging.INFO)

    def __get_supported_contributions(self):
        """
        Returns a dictionary of the supported contribution types and the respectively required predicates.
        """
        contribution_mapping = {
            "Definition": [self.terms["type"], self.terms["definition_content"]],
            "Dataset": [self.terms["type"], self.terms["dataset_name"], self.terms["dataset_domain"], self.terms["dataset_description"], self.terms["dataset_url"]],
            "Figure": [self.terms["type"], self.terms["figure_url"], self.terms["figure_mime"], self.terms["figure_description"]],
            "ExpResult": [self.terms["type"], self.terms["expresult_description"], self.terms["expresult_result"], self.terms["expresult_samplesize"]],
            "Software": [self.terms["type"], self.terms["software_name"], self.terms["software_description"], self.terms["software_url"]],
        }

        return contribution_mapping

    def __populate_scikg(self, bib_data: dict) -> Graph:

        scikg = Graph()

        for entry in bib_data:
            pub = self.publ[entry['ID']]

            # add metadata
            meta = self.publ[f"{entry['ID']}/meta"]

            scikg.add((pub, self.terms["has_meta_information"], meta))

            if "doi" in entry:
                scikg.add(
                    (meta, self.terms["has_doi"], Literal(entry["doi"])))

            if "title" in entry:
                scikg.add(
                    (meta, self.terms["has_title"], Literal(entry["title"])))

            if "year" in entry:
                scikg.add(
                    (meta, self.terms["has_publication_year"], Literal(entry["year"])))

            if "url" in entry:
                scikg.add(
                    (meta, self.terms["url"], Literal(entry["url"])))

            for author in entry["author"].split("and"):
                author = author.replace("\n", "").strip()
                author = re.sub(r"\s{2,}$", "", author)
                author = LatexNodes2Text().latex_to_text(author)
                author = author.replace(" ", "_")

                if author:
                    scikg.add(
                        (meta, self.terms["has_author"], URIRef(f"https://example.org/scikg/authors/{author}")))

            # add contributions
            if pub == self.publ["DBLP:conf/i-semantics/EhrlingerW16"]:
                contrib1 = self.publ[f"{entry['ID']}/contrib1"]

                scikg.add((pub, self.terms["has_contribution"], contrib1))
                scikg.add(
                    (contrib1, self.terms["type"], Literal("Definition")))
                scikg.add((contrib1, self.terms["definition_content"], Literal(
                    "A knowledge graph acquires and integrates information into an ontology and applies a reasoner to derive new knowledge.")))

            elif pub == self.publ["DBLP:conf/emnlp/LuanHOH18"]:
                contrib1 = self.publ[f"{entry['ID']}/contrib1"]

                scikg.add((pub, self.terms["has_contribution"], contrib1))
                scikg.add(
                    (contrib1, self.terms["type"], Literal("Dataset")))
                scikg.add(
                    (contrib1, self.terms["dataset_name"], Literal("SciERC")))
                scikg.add((contrib1, self.terms["dataset_domain"],
                           Literal("Artificial Intelligence")))
                scikg.add((contrib1, self.terms["dataset_description"], Literal(
                    "Our dataset (called SciERC) includes annotations for scientific entities, their relations, and coreference clusters for 500 scientific abstracts.")))
                scikg.add((contrib1, self.terms["dataset_url"], URIRef("https://paperswithcode.com/dataset/scierc")))

            elif pub == self.publ["Martin21"]:
                contrib1 = self.publ[f"{entry['ID']}/contrib1"]

                scikg.add((pub, self.terms["has_contribution"], contrib1))
                scikg.add(
                    (contrib1, self.terms["type"], Literal("Definition")))
                scikg.add((contrib1, self.terms["definition_content"], Literal(
                    "[...] knowledge graphs that result from transforming document-based publications will be referred to as RDF-transformed publications.")))

                contrib2 = self.publ[f"{entry['ID']}/contrib2"]

                scikg.add((pub, self.terms["has_contribution"], contrib2))
                scikg.add(
                    (contrib2, self.terms["type"], Literal("Figure")))
                scikg.add((contrib2, self.terms["figure_description"], Literal(
                    "A simple exemplary knowledge graph consisting of two RDF triples. The upper triple provides contextual information, the lower triple contentual information of the publication \\emph{{pub1}}. All non-literal triple members are identified using IRIs.")))
                scikg.add(
                    (contrib2, self.terms["figure_mime"], Literal("pdf")))
                scikg.add((contrib2, self.terms["figure_url"], Literal(
                    "/tex/example/figures/triple_example")))

            elif pub == self.publ["DBLP:journals/corr/abs-1809-06532"]:
                contrib1 = self.publ[f"{entry['ID']}/contrib1"]

                scikg.add((pub, self.terms["has_contribution"], contrib1))
                scikg.add(
                    (contrib1, self.terms["type"], Literal("Definition")))
                scikg.add((contrib1, self.terms["definition_content"], Literal(
                    "Nanopublications [provide] a granular and principled way of publishing scientific (and other types of) data in a provenance-centric manner. Such a nanopublication consists of an atomic snippet of a formal statement [...] that comes with information about where this knowledge came from [...] and with metadata about the nanopublication as a whole [...]. All these three parts are represented as Linked Data (in RDF) [...].")))

            elif pub == self.publ["DBLP:conf/amia/NoyCFKTVM03"]:
                contrib1 = self.publ[f"{entry['ID']}/contrib1"]

                scikg.add((pub, self.terms["has_contribution"], contrib1))
                scikg.add(
                    (contrib1, self.terms["type"], Literal("Software")))
                scikg.add((contrib1, self.terms["software_description"], Literal(
                    "Prot\\'{e}g\\'{e}-2000 is an open-source tool that assists users in the construction of large electronic knowledge bases. It has an intuitive user interface that enables developers to create and edit domain ontologies.")))
                scikg.add((contrib1, self.terms["software_name"], Literal(
                    "Prot{\\'{e}}g{\\'{e}}-2000")))
                scikg.add((contrib1, self.terms["software_url"], Literal(
                    "https://protege.stanford.edu")))

        return scikg

    def __validate_export(self, subject, tuples) -> bool:
        """
        Checks if a contribution to be exported represented by a subject and predicate
        object tuples is valid.
        """

        valid = True

        predicate_object_dict = {tuple[0]: tuple[1] for tuple in tuples}
        export_type = predicate_object_dict["https://example.org/scikg/terms/type"]

        included_predicates = sorted(predicate_object_dict.keys())
        necessary_predicates = sorted(
            [str(elem) for elem in self.supported_contributions[export_type]])

        if included_predicates != necessary_predicates:
            diff = set(necessary_predicates).difference(
                set(included_predicates))

            logging.warning(
                f"Export of {subject} is skipped due to missing predicates: {', '.join(list(diff))}")

            valid = False

        return valid

    
    def __store_graph(self, graph, exportpath) -> None:
        with open(exportpath, "w+") as file:
            file.write(graph.serialize(format="ttl"))

    
    def __clean_snippet(self, snippet) -> str:
        snippet = re.sub(r" {2,}", "", snippet)
        snippet = snippet.strip()

        return snippet
    

    def build(self) -> None:
        """
        Wrapper method for rebuilding the MinSKG.
        """

        logging.info("Parsing bib file...")
        parser = BibTexParser(common_strings=False)
        parser.ignore_nonstandard_types = False

        with open("/tex/example/example.bib") as bibtex_file:
            bib_data = bibtexparser.load(bibtex_file, parser)

        logging.info("Building MinSKG...")
        self.skg = self.__populate_scikg(bib_data.entries)

        logging.info("Storing MinSKG...")
        self.__store_graph(self.skg, "./minskg.ttl")


    def get_subgraph_for_subject(self, subject: str) -> str:
        """
        Returns the subgraph where the specified subject is the root node.
        """

        query = f"""
        prefix x: <urn:ex:>

        construct {{?s ?p ?o}}
        where {{
          <{subject}> (x:|!x:)* ?s .
          ?s ?p ?o .
        }}
        """

        result = self.skg.query(query)
        triples = list({(str(s), str(p), str(o)) for s, p, o in result})

        import_triples = list(filter(lambda x: x[1] == "https://example.org/scikg/terms/type", triples))

        if len(import_triples) != 1:
            raise Exception("Contribution lacks type information!")

        contribution_data = {triple[1]: triple[2] for triple in triples}

        return contribution_data
    

    def generate_content_snippet(self, label, citation_key, contribution_data) -> str:
        """
        Returns the content snippet.
        """

        contribution_type = contribution_data["https://example.org/scikg/terms/type"]
        required_props = [str(prop) for prop in self.supported_contributions[contribution_type]]

        if not set(required_props).issubset(contribution_data.keys()):
            print(set(required_props))
            print(contribution_data.keys())
            raise Exception("Data of contribution to be imported is incomplete.")

        if contribution_type == "Dataset":
            snippet = f"""
    % RDFtex Dataset Import Start
    \\begin{{dataset}}
    {contribution_data["https://example.org/scikg/terms/dataset_name"]}~\\cite{{{citation_key}}}\\\\
    Available at: \\url{{{contribution_data["https://example.org/scikg/terms/dataset_url"]}}}\\\\
    Domain: {contribution_data["https://example.org/scikg/terms/dataset_domain"]}\\\\
    Description: ``{contribution_data["https://example.org/scikg/terms/dataset_description"]}"~\\cite{{{citation_key}}}
    \\label{{{label}}}
    \\end{{dataset}}
    % RDFtex Dataset Import End
    """

        elif contribution_type == "Definition":
            snippet = f"""
    % RDFtex Definition Import Start
    \\begin{{definition}}
    \\label{{{label}}}
    {contribution_data["https://example.org/scikg/terms/definition_content"]}\\normalfont{{~\\cite{{{citation_key}}}}}
    \\end{{definition}}
    % RDFtex Definition Import End
    """

        elif contribution_type == "ExpResult":
            snippet = f"""
    % RDFtex ExpResult Import Start
    \\begin{{figure}}[htb!]
    \\centering
    \\includegraphics[width=0.7\\columnwidth]{{{contribution_data["https://example.org/scikg/terms/figure_url"]}}}
    \\caption{{{contribution_data["https://example.org/scikg/terms/figure_description"]} (Figure and caption adopted from~\\cite{{{citation_key}}}.)}}
    \\label{{{label}}}
    \\end{{figure}}
    % RDFtex ExpResult Import End
    """

        elif contribution_type == "Figure":
            snippet = f"""
    % RDFtex Figure Import Start
    \\begin{{figure}}[htb!]
    \\centering
    \\includegraphics[max width=0.7\\columnwidth]{{{contribution_data["https://example.org/scikg/terms/figure_url"]}}}
    \\caption{{{contribution_data["https://example.org/scikg/terms/figure_description"]} (Figure and caption adopted from~\\cite{{{citation_key}}}.)}}
    \\label{{{label}}}
    \\end{{figure}}
    % RDFtex Figure Import End
    """

        elif contribution_type == "Software":
            snippet = f"""
    % RDFtex Software Import Start
    \\begin{{software}}
    {contribution_data["https://example.org/scikg/terms/software_name"]}~\\cite{{{citation_key}}}\\\\
    Available at: \\url{{{contribution_data["https://example.org/scikg/terms/software_url"]}}}\\\\
    Description: ``{contribution_data["https://example.org/scikg/terms/software_description"]}"~\\cite{{{citation_key}}}
    \\label{{{label}}}
    \\end{{software}}
    % RDFtex Software Import End
    """

        return self.__clean_snippet(snippet)
    
    def generate_env_snippets(self) -> dict:
        """
        Returns the custom LaTeX environments used for the snippets.
        """

        dataset_env = """
    \\newcounter{dataset}[section]
    \\newenvironment{dataset}[1][]{\\refstepcounter{dataset}\\par\\medskip
    \\textbf{Dataset~\\thedataset. #1} \\rmfamily}{\\medskip}

    \\crefname{dataset}{Dataset}{Datasets}  
    \\Crefname{dataset}{Dataset}{Datasets}
    """

        expresult_env = """
    \\newcounter{expresult}[section]
    \\newenvironment{expresult}[1][]{\\refstepcounter{expresult}\\par\\medskip
    \\textit{Experimental Result~\\thedataset. #1} \\rmfamily}{\\medskip}
    """

        figure_env = """
    \\usepackage[export]{adjustbox}
    """

        software_env = """
    \\newcounter{software}[section]
    \\newenvironment{software}[1][]{\\refstepcounter{software}\\par\\medskip
    \\textbf{Software~\\thesoftware. #1} \\rmfamily}{\\medskip}

    \\crefname{software}{Software}{Software}  
    \\Crefname{software}{Software}{Software}
    """
        
        custom_envs = {"Dataset": dataset_env, "ExpResult": expresult_env,
        "Figure": figure_env, "Software": software_env}
        
        custom_envs = {import_type: self.__clean_snippet(snippet) for import_type, snippet in custom_envs.items()}
        
        return custom_envs
    

    def validate_exports(self, exports):
        validated_exports = dict(filter(lambda export: self.__validate_export(*export), exports.items()))

        return validated_exports
    