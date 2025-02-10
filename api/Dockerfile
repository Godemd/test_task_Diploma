FROM app/app_base

# Создание рабочего каталога
RUN mkdir -p /app/api
WORKDIR /app/api

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    dos2unix

# Копирование и установка requirements
COPY ./requirements.txt /app/api/requirements.txt
RUN pip install -r requirements.txt

# Копирование приложения
COPY ./ /app/api

# Правильное копирование и настройка entrypoint
COPY docker-entrypoint.sh /app/api/docker-entrypoint.sh
# Конвертация entrypoint в UNIX формат и установка прав
RUN dos2unix /app/api/docker-entrypoint.sh && \
    chmod +x /app/api/docker-entrypoint.sh

# Использование полного пути и явное указание оболочки
ENTRYPOINT ["/bin/bash", "/app/api/docker-entrypoint.sh"]