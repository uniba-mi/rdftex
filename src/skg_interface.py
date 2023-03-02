#!/usr/bin/env python3

class SkgInterface:
    """
    The SciKG interface.
    """

    def __get_supported_contributions(self):
        """
        Returns a dictionary of the supported contribution types and the respectively required predicates.
        """
        pass

    def __validate_export(self, subject, tuples) -> bool:
        """
        Checks if a contribution to be exported represented by a subject and predicate
        object tuples is valid.
        """
        pass

    def __store_graph(self, graph, exportpath) -> None:
        """
        Serializes and stores a graph at the specified path.
        """
        pass
            
    def get_subgraph_for_subject(self, subject: str) -> dict:
        """
        Returns the subgraph where the specified subject is the root node.
        """
        pass

    def generate_snippet(self, import_label, citation_key, import_type, contribution_data) -> str:
        """
        Returns the content snippet.
        """
        pass

    def get_custom_envs(self) -> dict:
        """
        Returns the custom LaTeX environments used for the snippets.
        """

    def generate_exports_document(self, exports: dict, exportsfilepath: str) -> None:
        """
        Generates a knowledge graph based on the exports of the preprocessed publication.
        """
        pass
