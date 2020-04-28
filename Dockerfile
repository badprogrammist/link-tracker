FROM python:3.8-alpine

WORKDIR /usr/app

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY ./ ./

ENV LOG_LEVEL=INFO
ENV ADDRESS=0.0.0.0:8000

CMD gunicorn main:app         \
      --log-level $LOG_LEVEL  \
      --bind $ADDRESS         \
      --access-logfile -      \
      --error-logfile -       \
      --workers=1