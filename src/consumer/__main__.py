import pika
from argparse import ArgumentParser
import logging


def main(argv=None):
    args_parser = ArgumentParser(__package__)
    args_parser.add_argument('routing_key', help='route queue to listen')
    args_parser.add_argument('--broker-host', default='localhost')
    args_parser.add_argument('--exchange-name', default='my-exchange')
    args_parser.add_argument('--queue-name', help='queue name to bind', default='')
    args_parser.add_argument('--durable', action='store_true', default=False)
    args_parser.add_argument('--auto-ack', action='store_true', default=False)
    # args_parser.add_argument('--log-level', help='log level', default='INFO')
    args_parser.add_argument
    args = args_parser.parse_args(argv)

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    if argv:
        logger.info('argv: %s', argv)
    logger.info('Routing keys: %s' % args.routing_key)

    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=args.broker_host))
    channel = connection.channel()

    channel.exchange_declare(exchange=args.exchange_name, exchange_type='direct')

    result = channel.queue_declare(queue=args.queue_name, durable=args.durable)
    queue_name = result.method.queue

    channel.queue_bind(
        exchange=args.exchange_name, queue=queue_name, routing_key=args.routing_key)

    logger.info(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        from time import sleep
        logger.info(" [x] %r:%r" % (method.routing_key, body))
        sleep(5)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=args.auto_ack)

    channel.start_consuming()
    
if __name__ == '__main__':
    main()