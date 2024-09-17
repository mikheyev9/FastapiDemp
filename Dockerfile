FROM python:3.11
WORKDIR /fastapi_app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --verbose
COPY . .
RUN chmod +x /fastapi_app/start.sh
CMD ["./start.sh"]
