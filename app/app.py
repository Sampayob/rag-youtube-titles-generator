"""App module"""

import os
import uuid
import warnings

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import psycopg2

from rag import rag_function
import db

app = Flask(__name__)

load_dotenv()

INDEX_NAME = os.getenv("INDEX_NAME")
APP_PORT = os.getenv("APP_PORT")


@app.route("/query", methods=["POST"])
def handle_query():
    data = request.json
    query = data["query"]

    if not query:
        return jsonify({"error": "No query provided"}), 400

    query_id = str(uuid.uuid4())

    title = rag_function(query)

    result = ({
        "conversation_id": query_id,
        "title": title
    })

    try:
        db.save_query(query_id=query_id,
                      query=query,
                      answer_data=title)
    except psycopg2.OperationalError as e:
        print(e)

    return jsonify(result)


@app.route("/feedback", methods=["POST"])
def handle_feedback():
    data = request.json
    query_id = data["query_id"]
    feedback = data["feedback"]

    if not query_id or feedback not in [1, -1]:
        return jsonify({'error': 'Invalid input'}), 400

    result = {
        "message": f"Feedback: query_id: {query_id}, feedback: {feedback}"
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=APP_PORT)
