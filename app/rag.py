"""RAG Module"""

import os

from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from elasticsearch import Elasticsearch
from ingest import load_index


load_dotenv()

INDEX_NAME = os.getenv("INDEX_NAME")

client = OpenAI()

prompt_template = """
You're a professional youtuber. Answer with a youtube video title to the QUERY which is based on the CONTEXT from the video database.
Use only the facts from the CONTEXT when answering the QUERY

QUERY:
{query}

CONTEXT:
{context}
""".strip()

entry_template = """
video_title: {title},
video_description: {description},
video_tags: {tags}
""".strip()


def build_prompt(query: str,
                 search_results: list,
                 prompt_template: str = prompt_template,
                 entry_template: str = entry_template
                 ) -> str:
    """
    Build a prompt whith the input query, search results and templates

    :param query: data query to be searched in the index
    :param search_results: search index results
    :param prompt_template: prompt template
    :param entry_template: record entry template

    :returns: prompt
    """
    context = ""

    for doc in search_results:
        context = context + entry_template.format(id=doc["id"],
                                                  title=doc["title"],
                                                  description=doc["description"],
                                                  tags=doc["tags"]) + "\n\n"

    prompt = prompt_template.format(query=query, context=context).strip()
    return prompt


def search(index_name: str, es_client: Elasticsearch, query: str) -> list:
    """
    Search a query in the Elasticsearch client index

    :param index_name: the index name.
    :param es_client: The Elasticsearch client interface.
    :param query: data query to be searched in the index

    :returns: list of results
    """
    search_query = {
        "size": 10,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["description", "text", "tags"],
                        "type": "best_fields"
                    }
                },
            }
        }
    }

    search_results = es_client.search(index=index_name, body=search_query)
    return [r['_source'] for r in search_results['hits']['hits']]


def llm(prompt: str, model='gpt-4o-mini') -> str:
    """
    Returns the response message to a prompt from a LLM model

    :param prompt: input prompt to be feeded to the LLM model
    :param model: OpenAI LLM model to be used

    :returns: LLM response in string format
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def rag_function(query: str) -> str:
    """
    Returns the RAG flow answer

    :param query: data query to be searched in the index

    :results: LLM response in string format
    """
    es_client = load_index()

    search_results = search(index_name=INDEX_NAME,
                            es_client=es_client,
                            query=query)

    prompt = build_prompt(query=query,
                          search_results=search_results,
                          entry_template=entry_template,
                          prompt_template=prompt_template)

    answer = llm(prompt=prompt)
    return answer

