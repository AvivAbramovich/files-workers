from argparse import ArgumentParser

try:
    from src.ready_files_eh import ReadyFilesEventHandlerWrapper, asyncio, AIOWatchdog
    from src.worker import queue, NamedQueueWorker
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
    from src.ready_files_eh import ReadyFilesEventHandlerWrapper, asyncio, AIOWatchdog
    from src.worker import queue, NamedQueueWorker


if __name__ == '__main__':
    args_parser = ArgumentParser(__package__)
    args_parser.add_argument('path', help='path to observing')
    args_parser.add_argument('--num-workers', type=int, default=1)
    args = args_parser.parse_args()

    q = queue.Queue()

    class MyEventHandler(ReadyFilesEventHandlerWrapper):
        async def on_file_ready(self, file_path):
            print('received %s' % file_path)
            q.put(file_path)
    class Worker(NamedQueueWorker):
        async def work_on_item(self, item):
            print('Worker %s working on %s' % (self.name, item))
            # simulating some work...
            rom time import sleep
            sleep(3)
            print('Worker %s done with %s!' % (self.name, item))


    loop = asyncio.get_event_loop()
    watch = AIOWatchdog(args.path, event_handler=MyEventHandler())
    watch.start()

    workers = []
    for i in range(args.num_workers):
        name = 'worker %d' % (i+1)
        print('Start "%s"' % name)
        w = Worker(name, q)
        w.start()
        workers.append(w)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stop loop...')
        loop.stop()
        watch.stop()
        print('Stop workers...')
        for w in workers:
            w.stop()
        print('join workers...')
        for w in workers:
            w.join()
