try:
    from src.async_worker import *
except ImportError:
    import sys
    from os.path import dirname

    d = dirname(__file__)
    root = '..'
    if d:
        d = dirname(d)
        if d:
            root = d
        else:
            root = '.'

    sys.path.append(root)
    from src.async_worker import *

import asyncio
from queue import Queue
from argparse import ArgumentParser

if __name__ == '__main__':
    args_parser = ArgumentParser(__package__)
    args_parser.add_argument('-n', metavar='NUM_WORKERS', type=int, default=1)
    args_parser.add_argument('-w', metavar='WORKS', type=int, default=5)
    args = args_parser.parse_args()

    class MyQueueWorker(AsyncQueueWorker):
        def __init__(self, name, queue):
            super().__init__(queue)
            self.name = name

        async def work_on_item(self, item):
            if type(item) != int:
                print('%s - killed (input: %s)' % (self.name, item))
                self.stop()
                return

            print('%s sleep for %d seconds' % (self.name, item))
            await asyncio.sleep(item)
            print('%s woke up!' % self.name)

    q = Queue()

    workers = []
    for i in range(args.n):
        w = MyQueueWorker('worker %d' % (i+1), q)
        w.start()
        workers.append(w)

    for i in range(args.w):
        q.put(i+1)
    
    try:
        for w in workers:
            q.put('kill worker')
        for w in workers:
            print('join %s' % w.name)
            w.join()
    except KeyboardInterrupt:
        print('Keyboard interrupt. Stop workers...')
        for w in workers:
            w.stop()
    print('done!')
