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


@app.route("/query")
def query():
    """
    Returns the subgraph where the specified subject is the root node.
    """

    query = request.args.get("query")
    query_result = minskg.query(query).serialize(format="ttl")

    return query_result, 200


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
    Returns the custom LaTeX environments used for some snippets.
    """

    env_snippets = minskg.generate_env_snippets()

    return jsonify(env_snippets), 200


@app.route("/validated_exports", methods=["POST"])
def validated_exports():
    """
    Returns the validated exports.
    """

    exports = request.json
    validated_exports = minskg.validate_exports(exports)

    return jsonify(validated_exports), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
