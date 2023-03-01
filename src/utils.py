"""Utility module for common tasks."""
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
        raise Exception("Data of contribution lacks type information.")

    snippet = skg_wrapper.generate_snippet(import_label, citation_key, import_type, contribution_data)

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
\\textbf{Software~\\thesoftware. #1} \\rmfamily}{\\medskip}

\\crefname{software}{Software}{Software}  
\\Crefname{software}{Software}{Software}
"""

    custom_envs = {"Dataset": dataset_env, "ExpResult": expresult_env,
                   "Figure": figure_env, "Software": software_env}

    for import_type in imported_types:
        if import_type in custom_envs:
            processed_lines.insert(
                preamble_end_index, custom_envs[import_type])
