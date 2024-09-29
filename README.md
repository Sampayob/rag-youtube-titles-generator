# Youtube 1M video title generator

A YouTube video titles generator which aims to create a viral title like the ones with >1M views.

## Problem Description

This project tackles the task of generating creative YouTube video titles based on the video description and/or metadata. It aims to assist YouTubers in creating catchy titles that will attract viewers and improve click-through rates.

## Objective

- The primary objective of this project is to develop a robust and effective YouTube title generator capable of producing creative and engaging titles for videos.
- By leveraging the power of natural language processing and machine learning, the model aims to assist YouTubers in creating titles that resonate with viewers and increase video visibility.

## Expected Outcomes

- A well-trained YouTube title generator capable of generating creative and engaging titles which hopefully helps to achieve a >1M views video.
- Improved click-through rates and video visibility for YouTubers.
- Insights into the factors that contribute to successful YouTube titles.

## Potential Applications

- YouTube content creators: Assisting YouTubers in creating titles that attract viewers and increase engagement.
- Video marketing platforms: Providing tools for optimizing video titles for search engine optimization and audience engagement.
- Content analysis tools: Analyzing YouTube video titles to understand trends and viewer preferences.

## Dataset

The project utilizes a dataset of YouTube videos retrieved from Kaggle. The dataset includes various features:

- `video_id`: Unique identifier for the video.
- `trending_date`: Date when the video started trending.
- `title`: Original title of the video.
- `channel_title`: Name of the Youtube channel that uploaded the video.
- `category_id`: Category associated with the video (e.g., 24 for entertainment).
- `publish_time`: Time and date the video was published.
- `tags`: List of keywords associated with the video.
- `views`: Number of views the video has received.
- `likes`: Number of likes the video has received.
- `dislikes`: Number of dislikes the video has received.
- `comment_count`: Number of comments on the video.
- `thumbnail_link`: Link to the video's thumbnail image.
- `comments_disabled`: Boolean indicating if comments are disabled.
- `ratings_disabled`: Boolean indicating if ratings are disabled.
- `video_error_or_removed`: Boolean indicating if the video has errors or was removed.
- `description`: Description text associated with the video.

Only some of them are used: `title`, `description`, `tags`, `views`, `likes`.

## Methodology

1. **Data Acquisition and Preprocessing**

- Data Download
  - The project utilizes the Kaggle API to download the "youtube-new" dataset containing video information.

- Data Cleaning
  - Videos with less than 1 million views are discarded.
  - Data is sorted by trending date, views, and likes to prioritize popular videos.
  - Entries with missing titles, tags, or descriptions are removed.
  - Duplicate entries (based on title and tags) are eliminated.

2. **RAG Model**
- Elasticsearch is used as a search engine for efficient retrieval of video data from the previous processed one.
- OpenAI's GPT-4o-mini model is used for large language model (LLM) tasks.
- The RAG model retrieves relevant videos based on the query and builds a prompt incorporating the retrieved context.
Finally, it calls the LLM to generate a title based on the combined information.

## Technologies

* [Elasticsearch]() - for text search
* OpenAI API as an LLM
* Flask as the API interface (see [Official Flask documentation](https://flask.palletsprojects.com/))


## Configure global variables

* Create a `.env` file in the project root directory with the global variables defined below.
* All the defined global variables do not need modifications, **except for the OpenAI API key, which is needed to run the LLM model.**

```
# App configuration
APP_PORT=9696
INDEX_NAME=youtube-titles
DATA_PATH=data/data.csv

# PostgreSQL Configuration
POSTGRES_HOST=postgres
POSTGRES_DB=course_assistant
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_PORT=5432

# Elasticsearch Configuration
ELASTIC_URL_LOCAL=http://localhost:9200
ELASTIC_URL=http://elasticsearch:9200
ELASTIC_PORT=9200

# OpenAI API Key
OPENAI_API_KEY=
```

## Running it with Docker

The easiest way to run the app its with Docker:

First, download and run Elasticsearch in docker with the following command:

```bash
docker run -it \
    --rm \
    --name elasticsearch \
    -m 4GB \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    docker.elastic.co/elasticsearch/elasticsearch:8.4.3
```

Then, in a different terminal, inside the `app` directory, run the app docker image.

```bash
docker run -it --rm \
  --env-file ./.env \
  -p 9696:9696 \
  --network="host" \
  youtube-title-generator
```

## Running it locally

- Python version: 3.10
- Dependencies managing: `poetry`


### Installing the dependencies

If docker is not used, you need to manually prepare the environment and the next described sections.

Install poetry:
```bash
pip install poetry
```

From the projec root directory (in which `poetry.lock` and `pyproject.toml` are located) install the dependencies:
```bash
poetry install
```

Activate the virtual environment (**remember do to it every time**):
```bash
poetry shell
```

### Running the aplication

**Elasticsearch**: Download and run Elasticsearch in docker with the following command:

```bash
docker run -it \
    --rm \
    --name elasticsearch \
    -m 4GB \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    docker.elastic.co/elasticsearch/elasticsearch:8.4.3
```

**App**: In a different terminal, run the application locally:

```bash
poetry run python app.py
```

## Preparing the application

Before starting the app, initialize the database:

```bash
cd app
export POSTGRES_HOST=localhost
poetry run python db_prep.py
```

## Using the application

First, start the application either with docker-compose or locally as described in the previous sections.

**Testing**

```bash
URL=htpp://localphost:9696/query

QUERY = "Top five easiest recipes under 10 minutes"

DATA = '{
  {"query": "'${QUERY}'" }
}'

curl -X POST \
  -H "Content-Type: application/json" \
  -d "${QUERY}" \
  ${URL}/query
```

The returned data will look like this:
```json
{
  "conversation_id": 'b40900e1-7c69-467e-93bd-a530f8a3d92a',
  "title": '"Top 5 Quick and Easy Recipes You Can Make in Under 10 Minutes!"'
  }
```

Sending feedback:

```bash

FEEDBACK_DATA='{
  "conversation_id": "'${ID}'",
  "feedback": 1
}'

curl -X POST \
  -H "Content-Type: application/json" \
  -d "${FEEDBACK_DATA}" \
  ${URL}/feedback
```


The returned data will look like this:
```json
{
  "message": "Feedback received for conversation b40900e1-7c69-467e-93bd-a530f8a3d92a: feedback: 1"
    }
```

Alternatively, you can use [test.py](test.py) for testing it:

```bash
poetry run python test.py
```

### Misc

**Jupyter notebooks**: To run Jupyter notebooks for experiments:
```bash
poetry run jupyter notebook
```

## Interface

Flask for serving the application as an API.

Refer to the ["Running the aplication" section](#running-the-aplication) for more information.

## Ingestion

For the code for the ingestion script is in [app/ingest.py](app/ingest.py), which it's run on the startup of the app (in [app/app.py](app/app.py))

## Evaluation

For the code for evaluating system, check [lab/notebooks/rag_lab.ipynb](lab/notebooks/rag_lab.ipynb) notebook*.

**Ensure to have Elasticsearch running on the same port before running the notebook. Also, create the environment variable `OPENAI_API_KEY` with your personal OpenAI API key in the command line or in a `.env` file*.

### Retrieval

The metrics used to evaluate retrieval were:
- Hit Rate: the division of the total number of queries by the frequency with which the pertinent item appears in the top-N recommendations.
- Mean Reciprocal Rank (MRR): 
is a ranking quality metric. It considers the position of the first relevant item in the ranked list. You can calculate MRR as the mean of Reciprocal Ranks across all users or queries. A Reciprocal Rank is the inverse of the position of the first relevant item.

The elasticsearch approach gave the following results:

- `hit_rate`: 0.941
- `mrr`: 0.8764996031746036

### RAG flow
The metric used to evaluate the quality of the RAG flow was:
- LLM-as-a-Judge: solution that uses LLMs to evaluate LLM responses based on any specific criteria of your choice, which means using LLMs to carry out LLM (system) evaluation.

The RAG flow gave the following results:

Among 1000 records:

 - gpt-4o-mini:
    - X RELEVANT: 599 (60%)
    - Y PARTLY_RELEVANT: 330 (33%)
    - Z IRRELEVANT: 71 (7%)

### Monitoring

