FROM python:3.11
RUN apt-get update && apt-get install -y postgresql-client
WORKDIR /fastapi_app
RUN pip install poetry
COPY pyproject.toml ./
RUN poetry install --no-dev --verbose
COPY . .
RUN chmod +x /fastapi_app/start.sh
CMD ["./start.sh"]
