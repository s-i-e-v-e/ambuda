"""
Executes task in the background
"""
import json
from concurrent.futures import Future
from typing import Callable, Any
import concurrent.futures
from ambuda.std import kvs

executor = concurrent.futures.ThreadPoolExecutor(max_workers=16)

class TaskStatus:
    id: str
    current: int
    total: int
    percentage: float
    status: str
    message: str

    def __init__(self, id: str, current: int, total: int, status: str, message: str):
        self.id = id
        self.current = current
        self.total = total
        self.status = status
        self.message = message
        self.percentage = current / total * 100

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def from_json(json_str):
        x = json.loads(json_str)
        return TaskStatus(x['id'], x['current'], x['total'], x['status'], x['message'])


def ts_get(task_id: str) -> TaskStatus:
    x = kvs.get(task_id)
    return TaskStatus.from_json(x) if x else TaskStatus('', 0, 1, '', '')


def ts_set(task_id: str, current: int, total: int, status: str = '', message: str = ''):
    kvs.set(task_id, TaskStatus(task_id, current, total, status, message).json())


def exec(f: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    fut = executor.submit(f, *args, **kwargs)
    fut.add_done_callback(done)


def done(fut: Future) -> Any:
    print(fut._state)
    print(fut.result())
    return fut.done()


def status():
    print('pending:', executor._work_queue.qsize(), 'jobs')
    print('threads:', len(executor._threads))
