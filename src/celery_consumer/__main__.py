from kombu import Connection, Exchange, Queue
from celery import Celery
from argparse import ArgumentParser
import logging


def main(argv=None):
    args_parser = ArgumentParser(__package__)
    args_parser.add_argument('routing_key', help='route queue to listen')
    args_parser.add_argument('--rabbitmq', default='localhost')
    args_parser.add_argument('--exchange', default='my-exchange')
    # args_parser.add_argument('--log-level', help='log level', default='INFO')
    args_parser.add_argument
    args = args_parser.parse_args(argv)

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    if argv:
        logger.info('argv: %s', argv)
    logger.info('Routing keys: %s' % args.routing_key)

    app = Celery('tasks', broker=args.rabbitmq)
    exchange = Exchange(args.exchange, type='direct')

    app.conf.task_queues = (
        Queue('', Exchange('default'), routing_key=args.routing_key),
    )
    # app.conf.task_default_queue = 'default'
    # app.conf.task_default_exchange_type = 'direct'
    # app.conf.task_default_routing_key = 'default'

    # logger.info(' [*] Waiting for logs. To exit press CTRL+C')

    # @app.task
    # def callback(ch, method, properties, body):
    #     logger.info(" [x] %r:%r" % (method.routing_key, body))


    # channel.basic_consume(
    #     queue=queue_name, on_message_callback=callback, auto_ack=True)

    # channel.start_consuming()
    
if __name__ == '__main__':
    main()