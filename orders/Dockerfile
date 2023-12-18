FROM tiangolo/uwsgi-nginx-flask:python3.8

ARG ENVIRONMENT

ENV SERVICE_NAME="orders"
ENV ENVIRONMENT=${ENVIRONMENT}
ENV FLASK_ENV=${ENVIRONMENT}
ENV UWSGI_INI uwsgi.ini

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app