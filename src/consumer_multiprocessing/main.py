import pika
from argparse import ArgumentParser
import logging
from logging.handlers import QueueHandler, QueueListener
import multiprocessing
from time import sleep

def consume(broker_host, exchange_name, routing_key, queue_name, durable, auto_ack):
    logging.info('hi')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    cp = pika.ConnectionParameters(host=broker_host)
    connection = pika.BlockingConnection(cp)
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

    result = channel.queue_declare(queue=queue_name, durable=durable)
    queue_name = result.method.queue

    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key)

    def callback(ch, method, properties, body):
        from time import sleep
        logger.info(" [x] %r:%r" % (method.routing_key, body))
        sleep(5)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=auto_ack)

    logger.info(' [*] Waiting for logs. To exit press CTRL+C')

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info('Shutting down...')

def logger_init():
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(asctime)s - %(process)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # ql gets records from the queue and sends them to the handler
    q = multiprocessing.Queue()
    ql = QueueListener(q, handler)
    ql.start()

    return logger, q

def worker_init(q):
    # all records from worker processes go to qh and then into q
    qh = QueueHandler(q)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(qh)

def main(argv=None):
    args_parser = ArgumentParser(__package__)
    args_parser.add_argument('--routing-key', help='route queue to listen', default='')
    args_parser.add_argument('--workers', type=int, help='number of workers', default=1)
    args_parser.add_argument('--broker-host', default='localhost')
    args_parser.add_argument('--exchange-name', default='my-exchange')
    args_parser.add_argument('--queue-name', help='queue name to bind', default='')
    args_parser.add_argument('--durable', action='store_true', default=False)
    args_parser.add_argument('--auto-ack', action='store_true', default=False)
    # args_parser.add_argument('--log-level', help='log level', default='INFO')
    args_parser.add_argument
    args = args_parser.parse_args(argv)

    logger, q = logger_init()

    if argv:
        logger.info('argv: %s', argv)
    logger.info('Routing keys: %s' % args.routing_key)
    
    logger.info('start pool with %d processes', args.workers)
    pool = multiprocessing.Pool(args.workers, worker_init, [q])
    for i in range(0, args.workers):
        pool.apply_async(consume, args=(
            args.broker_host, args.exchange_name, args.routing_key, 
            args.queue_name, args.durable, args.auto_ack))

    # Stay alive
    logger.info('start loop')
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        logger.info(' [*] Exiting...')
        pool.terminate()
        pool.join()

if __name__ == '__main__':
    main()