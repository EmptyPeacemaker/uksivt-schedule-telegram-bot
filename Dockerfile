FROM python:3.11.1-slim

WORKDIR /bot

COPY main.py .
COPY pyproject.toml .
COPY poetry.lock .

RUN pip install poetry
RUN poetry config virtualenvs.create false --local
RUN poetry install --no-dev --no-root --remove-untracked

ENV TG_KEY=CHANGEME

CMD python main.py