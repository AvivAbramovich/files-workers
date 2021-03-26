from src.worker import Worker
import asyncio
from threading import Thread

class AsyncWorker(Worker):    
    def _worker(self):
        async def inner_worker():
            while True:
                if not self._should_run:
                    break
                try:
                    await self.work()
                except Exception as e:
                    print('Fatal error: %s' % str(e))
                    self.stop()
                await asyncio.sleep(self.sleep_between_iterations)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(inner_worker())
        loop.close()

    async def work(self): pass

    def start(self):
        self._should_run = True
        self._thread.start()
    
    def stop(self):
        self._should_run = False
    
    def join(self):
        self._thread.join()

class AsyncQueueWorker(AsyncWorker):
    def __init__(self, queue, sleep_between_iterations=1):
        super().__init__(sleep_between_iterations)
        self._queue = queue
    
    async def work_on_item(self, item): pass

    async def on_empty_queue(self): pass

    async def work(self):
        try:            
            await self.work_on_item(self._queue.get(False))
        except queue.Empty:
            await self.on_empty_queue()
