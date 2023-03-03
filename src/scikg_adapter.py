"""Adapter module for interacting with SciKGs."""

import requests
import json
from constants import EXPORTS_SCIKG

def retrieve_content_snippet(label: str, citation_key: str, contribution_iri: str, skg: str) -> str:
    """
    Generates a LaTeX snippet based on the specified contribution data, import label,
    and citation key.
    """

    if skg == "MinSKG":
        payload = {"label": label, "citation_key": citation_key, "contribution_iri": contribution_iri, "skg": skg}
        response = requests.get("http://localhost:5000/content_snippet", params=payload).json()

        content_snippet = response["content_snippet"]
        contribution_type = response["contribution_type"]
    else:
        raise NotImplementedError("Only the MinSKG is currently supported for importing contributions.")

    return content_snippet, contribution_type


def retrieve_env_snippets(imported_types, skg):
    if skg == "MinSKG":
        response = requests.get("http://localhost:5000/env_snippets").json()

        required_custom_envs = {key: response[key] for key in imported_types if key in response}
    else:
        raise NotImplementedError("Only the MinSKG is currently supported for importing contributions.")
    
    return required_custom_envs


def retrieve_validated_exports(exports):
    if EXPORTS_SCIKG == "MinSKG":
        validated_exports = requests.post("http://localhost:5000/validated_exports", json=exports).json()
    else:
        raise NotImplementedError("Only the MinSKG is currently supported for importing contributions.")

    return validated_exports
