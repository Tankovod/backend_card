###############
#   BUILDER   #
###############

# Получаем официальное изображение из Docker-hub
FROM python:3.11-slim as builder

# Указываем рабочую дирректорию
WORKDIR /usr/src/app

# Указываем виртуальные переменные для докера и питона
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Линтер и автотесты \
RUN pip install --upgrade pip

RUN pip install flake8

COPY .. .
# Установка зависимости в сборщик
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt
# Проверка на стандарт написания кода
COPY .. .
# RUN flake8 --ignore=E501,F401 .

###############
#    FINAL    #
###############

# Получаем официальное изображение из Docker-hub
FROM python:3.11-slim

# Создаем рабочую дирректорию
RUN mkdir -p /home/app/

# Создаем пользователя с правами
RUN adduser app && usermod -aG sudo app

# Создание переменных для сборки
ENV HOME=/home/app
ENV APP_HOME=/home/app/src
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Установка зависимостей в сборщик
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*


# Копируем проект
COPY .. $APP_HOME
# Выдаем права пользователя на весь проект
RUN chown -R app:app $APP_HOME

# Меняем пользователя
USER app