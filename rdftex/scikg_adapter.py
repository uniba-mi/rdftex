"""Adapter module for interacting with SciKGs."""

import requests
from constants import EXPORTS_SCIKG, EXPORTS_RDF_DOCUMENT_PATH

def retrieve_content_snippet(label: str, citation_key: str, contribution_iri: str, skg: str) -> str:
    """
    Generates a LaTeX snippet based on the specified contribution data, import label,
    and citation key.
    """

    if skg == "MinSKG":
        payload = {"label": label, "citation_key": citation_key, "contribution_iri": contribution_iri, "skg": skg}
        result = requests.get("http://localhost:5000/content_snippet", params=payload).json()

        content_snippet = result["content_snippet"]
        contribution_type = result["contribution_type"]
    else:
        raise NotImplementedError("Only the MinSKG is currently supported for importing contributions.")

    return content_snippet, contribution_type


def retrieve_env_snippets(imported_types, skg):
    if skg == "MinSKG":
        result = requests.get("http://localhost:5000/env_snippets").json()

        required_custom_envs = {key: result[key] for key in imported_types if key in result}
    else:
        raise NotImplementedError("Only the MinSKG is currently supported for importing contributions.")
    
    return required_custom_envs

            
def store_exports(exports):

    if EXPORTS_SCIKG == "MinSKG":
        payload = {"exports": exports, "exports_rdf_document_path": EXPORTS_RDF_DOCUMENT_PATH}

        requests.get("http://localhost:5000/env_snippets", params=payload)
    else:
        raise NotImplementedError("Only the MinSKG is currently supported for importing contributions.")
