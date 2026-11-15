# Используем легковесный образ
FROM python:3.11-slim

# Переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Рабочая директория внутри контейнера
WORKDIR /app

# Сначала только зависимости — этот слой кэшируется,
# пока requirements.txt не меняется
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Теперь исходный код
COPY . .

# Точка входа (exec-форма), путь относительно WORKDIR
CMD ["python", "src/etl_cleaner.py"]