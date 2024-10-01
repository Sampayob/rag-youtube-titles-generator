"""RAG Module"""

import os
from time import time
import json
from typing import Tuple

from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from elasticsearch import Elasticsearch
from data_prep import load_index


load_dotenv()

INDEX_NAME = os.getenv("INDEX_NAME")

prompt_template = """
You're a professional youtuber. Answer with a youtube video title to the QUERY which is based on the CONTEXT from the video database.
Use only the facts from the CONTEXT when answering the QUERY

QUERY:
{query}

CONTEXT:
{context}
""".strip()

evaluation_prompt_template = """
You are an expert evaluator for a Retrieval-Augmented Generation (RAG) system.
Your task is to analyze the relevance of the generated answer to the given query.
Based on the relevance of the generated answer, you will classify it
as "NON_RELEVANT", "PARTLY_RELEVANT", or "RELEVANT".

Here is the data for evaluation:

query: {query}
Generated Answer: {answer}

Please analyze the content and context of the generated answer in relation to the question
and provide your evaluation in parsable JSON without using code blocks:

{{
"Relevance": "NON_RELEVANT" | "PARTLY_RELEVANT" | "RELEVANT",
"Explanation": "[Provide a brief explanation for your evaluation]"
}}
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


def llm(prompt: str, model='gpt-4o-mini') -> Tuple[dict, dict]:
    """
    Returns the response message to a prompt from a LLM model

    :param prompt: input prompt to be feeded to the LLM model
    :param model: OpenAI LLM model to be used

    :returns: LLM response in string format
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content
    tokens_stats = {
        'prompt_tokens': response.usage.prompt_tokens,
        'completion_tokens': response.usage.completion_tokens,
        'total_tokens': response.usage.total_tokens
    }

    return answer, tokens_stats


def evaluate_relevance(query: str, answer: str) -> Tuple[dict, dict]:
    """
    Evaluate the answer relevance

    :param query: input query.
    :param answer: LLM answer.
    """
    prompt = evaluation_prompt_template.format(query=query, answer=answer)
    evaluation, tokens = llm(prompt, 'gpt-4o-mini')

    try:
        json_eval = json.loads(evaluation)
        return json_eval, tokens
    except json.JSONDecodeError:
        result = {
            "Relevance": "UNKNOWN",
            "Explanation": "Failed to parse evaluation"
        }
        return result, tokens


def rag_function(query: str) -> dict:
    """
    Returns the RAG flow answer

    :param query: data query to be searched in the index

    :results: LLM response in string format
    """
    start = time()
    es_client = load_index()

    search_results = search(index_name=INDEX_NAME,
                            es_client=es_client,
                            query=query)

    prompt = build_prompt(query=query,
                          search_results=search_results,
                          entry_template=entry_template,
                          prompt_template=prompt_template)

    model = 'gpt-4o-mini'
    answer, tokens_stats = llm(prompt=prompt, model=model)

    relevance, rel_tokens_stats = evaluate_relevance(query, answer)

    response_time = time() - start

    answer_data = {
        "answer": answer,
        "model_used": model,
        "response_time": response_time,
        "relevance": relevance.get("Relevance", "UNKNOWN"),
        "relevance_explanation": relevance.get("Explanation", "Failed to parse evaluation"),
        "prompt_tokens": tokens_stats['prompt_tokens'],
        "completion_tokens": tokens_stats['completion_tokens'],
        "total_tokens": tokens_stats['total_tokens'],
        "eval_prompt_tokens": rel_tokens_stats['prompt_tokens'],
        "eval_completion_tokens": rel_tokens_stats['completion_tokens'],
        "eval_tokens_tokens": rel_tokens_stats['total_tokens']
    }

    return answer_data
