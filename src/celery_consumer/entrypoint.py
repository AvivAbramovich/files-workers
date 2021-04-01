from os import getenv
from .__main__ import main

argv = [
    getenv('ROUTING_KEY')
]

def apply(key, arg_name):
    global argv
    val = getenv(key)
    if val:
        argv += [arg_name, val]

apply('RABBITMQ_HOST', '--rabbitmq')
apply('EXCHANGE', '--exchange')

main(argv)