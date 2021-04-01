from os import getenv
from .__main__ import main

argv = [getenv('WATCH_PATH')]

def apply(key, arg_name, parse=None):
    global argv
    val = getenv(key)
    if val:
        if parse:
            val = parse(val)
        else:
            val = [val]
        argv += [arg_name] + val

apply('RABBITMQ_HOST', '--rabbitmq')
apply('EXCHANGE', '--exchange')
apply('KEYS', '-k', lambda keys: keys.split(';'))

main(argv)