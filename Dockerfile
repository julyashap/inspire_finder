FROM python:3.11.9

WORKDIR /app

COPY /poetry.lock /pyproject.toml .

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    python3 -m pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . .
