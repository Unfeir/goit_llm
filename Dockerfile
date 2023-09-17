FROM python:3.10

RUN mkdir /goit_llm

COPY .env .

WORKDIR /goit_llm
ENV PYTHONPATH "${PYTHONPATH}:/goit_llm"

COPY pyproject.toml .


RUN pip install poetry

ADD pyproject.toml poetry.lock /code/
RUN poetry config virtualenvs.create false && poetry config installer.max-workers 10
RUN poetry install --no-root
RUN poetry shell

COPY ./app .
COPY ../migrations ./migrations
COPY alembic.ini .
COPY ../docker ./docker


CMD ["uvicorn", "utils.main:app", "--host", "0.0.0.0", "--reload", "--port", "8000"]

