FROM python:3.12.4

RUN pip install --upgrade pip && pip install poetry

WORKDIR /app

COPY pyproject.toml /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root

COPY . /app

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
