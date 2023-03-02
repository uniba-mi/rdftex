#!/usr/bin/env python3

from flask import Flask, jsonify, request
from minskg import MinSKG

app = Flask(__name__)
minskg = MinSKG()

@app.route("/")
def root():
    return "Hello from the MinSKG API."


@app.route("/build")
def build():
    minskg.build()

    return "MinSKG successfully built."


@app.route("/subgraph")
def subgraph():
    """
    Returns the subgraph where the specified subject is the root node.
    """

    subject = request.args.get("subject")

    contribution_data = minskg.get_subgraph_for_subject(subject)

    return jsonify(
        {
            "contribution_data": contribution_data,
        }
    ), 200


@app.route("/content_snippet")
def content_snippet():
    """
    Returns the content snippet.
    """

    label = request.args.get("label")
    citation_key = request.args.get("citation_key")
    contribution_iri = request.args.get("contribution_iri")

    contribution_data = minskg.get_subgraph_for_subject(contribution_iri)
    content_snippet = minskg.generate_content_snippet(label, citation_key, contribution_data)
    
    return jsonify(
        {
            "content_snippet": content_snippet,
            "contribution_type":  contribution_data["https://example.org/scikg/terms/type"]
        }
    ), 200


@app.route("/env_snippets")
def env_snippets():
    """
    Returns the custom LaTeX environments used for the snippets.
    """

    env_snippets = minskg.generate_env_snippets()

    return jsonify(
        env_snippets
    ), 200


@app.route("/exports_document")
def exports_document() -> None:
    """
    Generates the exports RDF document of the preprocessed publication.
    """

    exports = request.args.get("exports")
    exports_rdf_document_path = request.args.get("exports_rdf_document_path")

    minskg.generate_exports_rdf_document(exports, exports_rdf_document_path)

    return "Exports RDF document successfully generated."


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
