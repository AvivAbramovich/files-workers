FROM python:3.8-alpine

WORKDIR /code

ADD src/consumer/requirements.txt requirements.txt

RUN pip install -r requirements.txt 

ADD src src

ENV PYTHONUNBEFFERED=1
ENV CONSUMER_BROKER_HOST localhost
ENV CONSUMER_ROUTING_KEY ''
ENV CONSUMER_EXCHANGE_NAME exhange
ENV CONSUMER_QUEUE_NAME ''
ENV CONSUMER_DURABLE TRUE
ENV CONSUMER_AUTO_ACK FALSE

CMD python -m src.consumer.entrypoint