FROM python:3.10.11-slim

WORKDIR /app

RUN pip install poetry

COPY data/data.csv data/data.csv

COPY ["poetry.lock", "pyproject.toml", "./"]
RUN poetry config virtualenvs.create false
RUN poetry install

COPY app .

EXPOSE 9696

ENTRYPOINT gunicorn --bind 0.0.0.0:9696 app:app