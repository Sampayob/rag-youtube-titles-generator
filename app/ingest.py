"""Ingestion module"""

import os

import pandas as pd
from elasticsearch import Elasticsearch, BadRequestError
from dotenv import load_dotenv


load_dotenv()

INDEX_NAME = os.getenv("INDEX_NAME")
DATA_PATH = os.getenv("DATA_PATH")
ELASTIC_URL_LOCAL = os.getenv("ELASTIC_URL_LOCAL")


def load_documents_in_index(index_name: str,
                            es_client: Elasticsearch,
                            documents: dict
                            ) -> Elasticsearch:
    """
    Load documents in dict format into the Elasticsearch search client

    :param index_name: the index name.
    :param es_client: The Elasticsearch client interface.
    :param documents: documents in dict format.

    :returns: The Elasticsearch client interface with the documents indexed.
    """
    for doc in documents:
        es_client.index(index=index_name, document=doc)

    return es_client


def load_csv_to_records(data_path: str) -> dict:
    """
    Loads CSV file as a records dictionary

    :param data_path: path in which the CSV file is located.

    :returns: data records in dict format
    """
    df = pd.read_csv(data_path)
    return df[['id', 'title', 'tags', 'description']].to_dict(orient="records")


def load_index(data_path: str = DATA_PATH) -> Elasticsearch:
    """
    Loads RAG model data

    :param data_path: path in which the CSV file is located.

    :returns: Elasticserach client with loaded index
    """
    documents = load_csv_to_records(data_path)

    es_client = Elasticsearch(ELASTIC_URL_LOCAL)

    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0},
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "description": {"type": "text"},
                "tags": {"type": "text"},
                "id": {"type": "keyword"},
            }
        }
    }

    try:
        es_client.indices.create(index=INDEX_NAME, body=index_settings)
    except ConnectionError:
        es_client.options(ignore_status=[400, 404]).indices.delete(index=INDEX_NAME)
        es_client.indices.create(index=INDEX_NAME, body=index_settings)

    return load_documents_in_index(INDEX_NAME, es_client, documents)
