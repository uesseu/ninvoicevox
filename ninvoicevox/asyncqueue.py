'''
A queue object module for asynchronous in order processing.
When you use voice as alarm, multiple voices may played
simultaneously. This makes voice hard to listened.
It is not good.
AsyncQueue class in this module plays only one voice at once.
'''
from queue import Queue
from typing import Any, List
from threading import Thread

class AsyncQueue:
    '''
    Queue object to process something in order.
    It makes another thread and fire in order.
    This queue can append something after start running.
    Must end by end method or with statement.
    Used like below.

    ----------
    >>> import operator
    >>> aq = AsyncQueue()
    >>> aq.put(operator.add, 1, 3)
    >>> aq.start()  # It can start on any time.
    >>> print(aq.get())  # Get last result of put. It is synchronous.
    4
    >>> aq.put(operator.sub, 5, 3)
    >>> result = aq.end()  # Get results of aq.
    >>> print(result)
    [2]
    >>> with AsyncQueue() as aqueue:
    >>>     aqueue.put(operator.sub, 5, 3)  # Just calculate and discard it.

    ----------

    end_object: Any
        If it is got from queue, the procedure ends.
        It should be singleton.
    save_results: bool
        Save results. If it is True, result of operation
        will be saved and they can be retrived by AsyncQueue.end().
    endless: bool
        If it is True, this programm is not terminated.
        It may be good if you want to make daemon.
        If it is True, save_results forced to be false.
    '''
    def __init__(self, end_object: Any = None,
                 save_results: bool = False,
                 endless: bool = False):
        self.run = False
        self.queue: Queue = Queue()
        self.save_results = save_results
        self.end_object = end_object
        self.endless = endless
        self.results: List[Any] = []

    def repeat(self) -> None:
        '''
        Repeat processing data in queue.
        This should not be called if you want to
        process them asynchronously.
        '''
        while True:
            obj = self.queue.get()
            if not self.endless and obj is self.end_object:
                break
            result = obj[0](*obj[1:])
            if self.save_results:
                self.results.append(result)

    def start(self) -> 'AsyncQueue':
        '''
        Start processing repeatedly.
        '''
        self.thread = Thread(target=self.repeat)
        self.thread.start()
        return self

    def put(self, *data: Any) -> None:
        '''
        Put procedure into queue.

        First argument is function and following arguments are
        arguments for the function.
        '''
        self.queue.put(data)

    def get(self) -> Any:
        if self.save_results:
            return self.results.pop()

    def end(self) -> list:
        self.queue.put(None)
        self.thread.join()
        return self.results

    def __enter__(self) -> 'AsyncQueue':
        return self.start()

    def __exit__(self, i: Any, j: Any, k: Any) -> None:
        self.end()
