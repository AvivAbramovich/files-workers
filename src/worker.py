from threading import Thread, Lock
import queue
from time import sleep
import logging


class Worker:
    def __init__(self, sleep_between_iterations=1):
        self._thread = Thread(target=self._worker, args=())
        self._should_run = False
        self.sleep_between_iterations = sleep_between_iterations

    def _worker(self):
        while True:
            if not self._should_run:
                break
            try:
                self.work()
            except Exception as e:
                print('Fatal error: %s' % str(e))
                self.stop()
            sleep(self.sleep_between_iterations)
    
    def start(self):
        self._should_run = True
        self._thread.start()
    
    def stop(self):
        self._should_run = False
    
    def join(self):
        self._thread.join()

class QueueWorker(Worker):
    def __init__(self, queue, sleep_between_iterations=1):
        self._queue = queue
        super().__init__(sleep_between_iterations)
    
    def work_on_item(self, item): pass

    def on_empty_queue(self): pass

    def work(self):
        try:            
            self.work_on_item(self._queue.get(False))
        except queue.Empty:
            self.on_empty_queue()
