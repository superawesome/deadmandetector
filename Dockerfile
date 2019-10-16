FROM python:3.7-alpine

COPY . /app

WORKDIR /app

RUN apk --no-cache add gcc musl-dev && pip install -r requirements.txt && apk --no-cache del gcc musl-dev

EXPOSE 5000

ENV FLASK_APP=app.py

CMD flask run --host=0.0.0.0
