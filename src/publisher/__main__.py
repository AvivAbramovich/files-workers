import pika
import asyncio
from hachiko.hachiko import AIOWatchdog
from argparse import ArgumentParser
import re
from os.path import basename
import logging
from src.ready_files_handler import ReadyFilesEventHandlerWrapper


def main(argv=None):
    args_parser = ArgumentParser(__package__)
    args_parser.add_argument('path', help='path to observing')
    args_parser.add_argument('--rabbitmq', default='localhost')
    args_parser.add_argument('--exchange', default='my-exchange')
    args_parser.add_argument('-k', metavar='KEYS', help='keys for file names', nargs='+', default=[])
    # args_parser.add_argument('--log-level', help='log level', default='INFO')
    args_parser.add_argument
    args = args_parser.parse_args(argv)

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    if argv:
        logger.info('argv: %s', argv)
    logger.info('watching %s' % args.path)
    logger.info('Routing keys: %s' % args.k)

    routes = '|'.join(args.k) if args.k else '.*'
    pattern = '({routes})-.*'.format(routes=routes)
    logger.info('pattern: %s' % pattern)

    class MyEventHandler(ReadyFilesEventHandlerWrapper):
        async def on_file_ready(self, file_path):
            logger.info('received %s' % file_path)

            try:
                m = re.match(pattern, basename(file_path))
                if not m:
                    logger.info('ignore %s' % file_path)
                    return

                routing_key = m.groups()[0]
                with pika.BlockingConnection(
                    pika.ConnectionParameters(host=args.rabbitmq)) as connection:
                    channel = connection.channel()

                    channel.exchange_declare(exchange=args.exchange, exchange_type='direct')

                    channel.basic_publish(
                        exchange=args.exchange, 
                        routing_key=routing_key, 
                        body=file_path
                    )
                    logger.info(" [x] Sent %r:%r" % (routing_key, file_path))
            except Exception as e:
                logger.exception(e)

    handler = MyEventHandler()

    loop = asyncio.get_event_loop()
    watch = AIOWatchdog(args.path, event_handler=handler)
    watch.start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stop loop...')
        watch.stop()
        loop.stop()
    
if __name__ == '__main__':
    main()