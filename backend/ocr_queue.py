"""索引期共用的有界 OCR 通路。队列只传图片路径与结果,不传 PDF 原生对象。"""
import os
import queue
import threading

import httpx

from . import config, ocr


_PRODUCER = None


class Producer:
    def __init__(self, requests, responses, capacity, stopped, slot):
        self.requests = requests
        self.responses = responses
        self.capacity = capacity
        self.stopped = stopped
        self.slot = slot
        self.sequence = 0
        self.pending = set()
        self.ready = {}

    def submit(self, render):
        self.collect_ready()
        while not self.capacity.acquire(timeout=.5):
            self.collect_ready()
            if self.stopped.is_set():
                raise RuntimeError("OCR 通路已停止")
        path = None
        try:
            if self.stopped.is_set():
                raise RuntimeError("OCR 通路已停止")
            path = render()
            self.sequence += 1
            task = self.sequence
            while True:
                try:
                    self.requests.put((self.slot, task, path), timeout=.5)
                    break
                except queue.Full:
                    if self.stopped.is_set():
                        raise RuntimeError("OCR 通路已停止")
            self.pending.add(task)
            return task
        except BaseException:
            if path:
                _unlink(path)
            self.capacity.release()
            raise

    def collect_ready(self):
        while True:
            try:
                task, text, error = self.responses.get_nowait()
            except queue.Empty:
                return
            self.ready[task] = (text, error)

    def completed(self):
        self.collect_ready()
        return set(self.ready)

    def receive(self, task):
        if task not in self.pending:
            raise ValueError(f"未知 OCR 任务: {task}")
        while task not in self.ready:
            try:
                done, text, error = self.responses.get(timeout=.5)
                self.ready[done] = (text, error)
            except queue.Empty:
                if self.stopped.is_set():
                    raise RuntimeError("OCR 通路已停止")
        self.pending.remove(task)
        return self.ready.pop(task)

    def finish(self):
        for task in list(self.pending):
            self.receive(task)


def initialize_worker(values, channels):
    global _PRODUCER
    config.override_local(values)
    requests, responses, capacity, stopped, counter = channels
    with counter.get_lock():
        slot = counter.value
        counter.value += 1
    _PRODUCER = Producer(requests, responses[slot], capacity, stopped, slot)


def producer():
    return _PRODUCER


def _unlink(path):
    try:
        os.unlink(path)
    except OSError:
        pass


class OCRPool:
    def __init__(self, context, parse_workers, workers):
        self.workers = workers
        self.requests = context.Queue(maxsize=workers)
        self.responses = [context.Queue() for _ in range(parse_workers)]
        self.capacity = context.BoundedSemaphore(workers * 2)
        self.stopped = context.Event()
        self.counter = context.Value("i", 0)
        self.threads = []

    @property
    def channels(self):
        return self.requests, self.responses, self.capacity, self.stopped, self.counter

    def _run(self):
        client = None
        try:
            while True:
                request = self.requests.get()
                if request is None:
                    return
                slot, task, path = request
                try:
                    if client is None:
                        client = httpx.Client(limits=httpx.Limits(max_connections=1,
                                                                max_keepalive_connections=1))
                    text, error = ocr.ocr_image(path, client=client)
                except Exception as exc:
                    text, error = "", f"{type(exc).__name__}: {exc}"
                finally:
                    _unlink(path)
                    self.capacity.release()
                self.responses[slot].put((task, text, error))
        finally:
            if client is not None:
                client.close()

    def __enter__(self):
        for number in range(self.workers):
            thread = threading.Thread(target=self._run, name=f"ocr-{number + 1}")
            thread.start()
            self.threads.append(thread)
        return self

    def __exit__(self, *_):
        self.stopped.set()
        for _ in self.threads:
            self.requests.put(None)
        for thread in self.threads:
            thread.join()
        self.requests.close()
        self.requests.join_thread()
        for channel in self.responses:
            # 子进程异常退出时可能无人再读取响应,不能等待 feeder 写满的管道。
            channel.cancel_join_thread()
            channel.close()
