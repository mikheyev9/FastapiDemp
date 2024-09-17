#!/bin/bash
if [ -f .env ]; then
  echo "Загрузка переменных окружения DB_HOST и DB_PORT из .env файла"
  export DB_HOST=$(grep '^DB_HOST=' .env | cut -d '=' -f2)
  export DB_PORT=$(grep '^DB_PORT=' .env | cut -d '=' -f2)
fi

# Проверка на наличие переменных DB_HOST и DB_PORT
if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ]; then
  echo "Ошибка: Необходимо задать DB_HOST и DB_PORT в файле .env"
  exit 1
fi

echo "Ожидание доступности базы данных PostgreSQL на ${DB_HOST}:${DB_PORT}..."

# Ожидание доступности базы данных PostgreSQL
while ! pg_isready -h $DB_HOST -p $DB_PORT; do
  echo "База данных недоступна, ожидание..."
  sleep 2
done

echo "База данных доступна!"
# Выполнение миграций Alembic
poetry run alembic upgrade head

# Запуск Gunicorn с UvicornWorker
poetry run gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
