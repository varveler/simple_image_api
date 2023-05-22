FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /src

# psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt /src/
RUN pip3 install -r requirements.txt

COPY . /src/

RUN chmod -R 777 /src/media/tempImageFiles
