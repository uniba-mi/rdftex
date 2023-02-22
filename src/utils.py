"""Utility module for common tasks."""

import re
import glob
from pyparsing import ParseException
from typing import Dict

from minskg import MinSKG

def generate_snippet(import_uri: str, import_label: str, citation_key: str, target_skg: str) -> str:
    """
    Generates a LaTeX snippet based on the specified contribution data, import label,
    and citation key.
    """

    if target_skg == "MinSKG":
        skg_wrapper = MinSKG()

    else:
        raise NotImplementedError("Only the MinSKG is currently supported for importing contributions.")

    import_type, contribution_data = skg_wrapper.get_subgraph_for_subject(import_uri)
    
    if not import_type:
        raise Exception("Data of contribution to be imported is incomplete.")
        
    if import_type == "Dataset":
        snippet = f"""
\\begin{{dataset}}
{contribution_data["https://example.org/scikg/terms/dataset_name"]}~\\cite{{{citation_key}}}\\\\
Domain: {contribution_data["https://example.org/scikg/terms/dataset_domain"]}\\\\
Description: ``{contribution_data["https://example.org/scikg/terms/dataset_description"]}"~\\cite{{{citation_key}}}
\\label{{{import_label}}}
\\end{{dataset}}
"""

    elif import_type == "Definition":
        snippet = f"""
\\begin{{definition}}
\\label{{{import_label}}}
{contribution_data["https://example.org/scikg/terms/definition_content"]}\\normalfont{{~\\cite{{{citation_key}}}}}
\\end{{definition}}
"""

    elif import_type == "ExpResult":
        snippet = f"""
\\begin{{figure}}[htb!]
\\centering
\\includegraphics[width=0.7\\columnwidth]{{{contribution_data["https://example.org/scikg/terms/figure_url"]}}}
\\caption{{{contribution_data["https://example.org/scikg/terms/figure_description"]} (Figure and caption adopted from~\\cite{{{citation_key}}}.)}}
\\label{{{import_label}}}
\\end{{figure}}
"""

    elif import_type == "Figure":
        figurepath = "/tex/" + \
            contribution_data["https://example.org/scikg/terms/figure_url"] + ".*"

        if not glob.glob(figurepath):
            raise NotImplementedError(
                "Currently only the import of locally stored figures is supported!")

        snippet = f"""
\\begin{{figure}}[htb!]
\\centering
\\includegraphics[max width=0.7\\columnwidth]{{{contribution_data["https://example.org/scikg/terms/figure_url"]}}}
\\caption{{{contribution_data["https://example.org/scikg/terms/figure_description"]} (Figure and caption adopted from~\\cite{{{citation_key}}}.)}}
\\label{{{import_label}}}
\\end{{figure}}
"""

    elif import_type == "Software":
        snippet = f"""
\\begin{{software}}
{contribution_data["https://example.org/scikg/terms/software_name"]}~\\cite{{{citation_key}}}\\\\
Available at: \\url{{{contribution_data["https://example.org/scikg/terms/software_url"]}}}\\\\
Description: ``{contribution_data["https://example.org/scikg/terms/software_description"]}"~\\cite{{{citation_key}}}
\\label{{{import_label}}}
\\end{{software}}
"""

    snippet = re.sub(r" {2,}", " ", snippet)

    return snippet, import_type


def add_custom_envs(processed_lines, preamble_end_index, imported_types) -> None:
    """
    Adds custom environments to the LaTeX project if necessary based on the types
    of the imported contributions.
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
\\textbf{Software~\\thedataset. #1} \\rmfamily}{\\medskip}

\\crefname{software}{Software}{Software}  
\\Crefname{software}{Software}{Software}
"""

    custom_envs = {"Dataset": dataset_env, "ExpResult": expresult_env,
                   "Figure": figure_env, "Software": software_env}

    for import_type in imported_types:
        if import_type in custom_envs:
            processed_lines.insert(
                preamble_end_index, custom_envs[import_type])
