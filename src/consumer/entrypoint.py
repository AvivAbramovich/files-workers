from os import getenv
from .__main__ import main

DEFAULT_FUNC = lambda key, val: [key, val]
def flag_func(k, v):
    if v.lower() == 'true':
        return [k]
    return []

argv = [
    getenv('CONSUMER_ROUTING_KEY')
]

def apply(key, arg_name, func=DEFAULT_FUNC):
    global argv
    val = getenv(key)
    if val:
        argv += func(arg_name, val)

apply('CONSUMER_BROKER_HOST', '--broker-host')
apply('CONSUMER_QUEUE_NAME', '--queue-name')
apply('CONSUMER_EXCHANGE_NAME', '--exchange-name')
apply('CONSUMER_DURABLE', '--durable', flag_func)
apply('CONSUMER_AUTO_ACK', '--auto-ack', flag_func)

main(argv)