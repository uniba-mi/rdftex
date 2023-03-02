"""Utility module for common tasks."""
from minskg import MinSKG
from constants import EXPORTS_SCIKG, EXPORTS_RDF_DOCUMENT_PATH

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


def get_custom_envs(imported_types, target_skg):
    if target_skg == "MinSKG":
        skg_wrapper = MinSKG()
    else:
        raise NotImplementedError("Only the MinSKG is currently supported for importing contributions.")
    
    custom_envs = skg_wrapper.get_custom_envs()
    required_custom_envs = {key: custom_envs[key] for key in imported_types if key in custom_envs}

    return required_custom_envs

            
def generate_exports_rdf_document(exports):

    if EXPORTS_SCIKG == "MinSKG":
        skg_wrapper = MinSKG()
    else:
        raise NotImplementedError("Only the MinSKG is currently supported for importing contributions.")
    
    skg_wrapper.generate_exports_document(exports, EXPORTS_RDF_DOCUMENT_PATH)

