FROM python:3.8-alpine

WORKDIR /code

ADD src/publisher/requirements.txt requirements.txt

RUN pip install -r requirements.txt 

ADD src src

ENV PYTHONUNBEFFERED=1
ENV RABBITMQ_HOST localhost
ENV WATCH_PATH .
ENV KEYS ''
ENV EXCHANGE exhange

CMD python -m src.publisher.entrypoint