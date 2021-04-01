FROM python:3.8-alpine

WORKDIR /code

ADD src/celery_consumer/requirements.txt requirements.txt

RUN pip install -r requirements.txt 

ADD src src

ENV PYTHONUNBEFFERED=1
ENV RABBITMQ_HOST localhost
ENV ROUTING_KEY ''
ENV EXCHANGE exhange

CMD python -m src.consumer.entrypoint