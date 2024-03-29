FROM python:3.7-alpine

COPY . /app

WORKDIR /app

RUN apk --no-cache add uwsgi uwsgi-python3 uwsgi-http && pip --no-cache-dir install -r requirements.txt

EXPOSE 8080

CMD uwsgi --plugin python3,http --http 0.0.0.0:8080 --wsgi-file app.py --callable app_dispatch -H /usr/local/ --processes 1 --threads 4 --uid nobody --master
