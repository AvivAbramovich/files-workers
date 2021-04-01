from hachiko.hachiko import asyncio, AIOWatchdog, AIOEventHandler

class ReadyFilesEventHandlerWrapper(AIOEventHandler):
    def __init__(self, sleep_time=0.1):
        super().__init__()
        self._active_events = {}
        self.sleep_time = sleep_time
    
    async def on_file_ready(self, file_path): pass

    async def _dispatch_work(self, event):
        if event.is_directory:
            return
        
        file_path = getattr(event, 'dest_path', event.src_path)

        if file_path in self._active_events:
            self._active_events[file_path] = True
        else:
            self._active_events[file_path] = True

            # break from this loop when self.sleep_time passes without other file modified or deleted events for this file
            while True:
                val = self._active_events.get(file_path)
                if val:
                    # turn active flag off and sleep 
                    self._active_events[file_path] = False
                    await asyncio.sleep(self.sleep_time)
                elif val is None:
                    # file deleted
                    return
                else:
                    # break from loop
                    break
            
            self._active_events.pop(file_path)
            await self.on_file_ready(file_path)

    async def on_created(self, event):
        await self._dispatch_work(event)

    async def on_modified(self, event):
        await self._dispatch_work(event)
    
    async def on_deleted(self, event):
        if event.src_path in self._active_events:
            self._active_events.pop(event.src_path)
    
    async def on_moved(self, event):
        if event.src_path in self._active_events:
            self._active_events.pop(event.src_path)
        await self._dispatch_work(event)


if __name__ == "__main__":
    from argparse import ArgumentParser
    args_parser = ArgumentParser(__name__)
    args_parser.add_argument('path', help='path to observing')
    args = args_parser.parse_args()

    class MyEventHandler(ReadyFilesEventHandlerWrapper):
        async def on_file_ready(self, file_path):
            print('received %s' % file_path)

    loop = asyncio.get_event_loop()
    watch = AIOWatchdog(args.path, event_handler=MyEventHandler())
    watch.start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Stop loop...')
        watch.stop()
        loop.stop()
