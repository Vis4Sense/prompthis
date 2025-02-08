"""
This module contains the RequestQueue class which manages a queue of requests.
"""

import queue
import threading
from datetime import datetime
import requests
import pytz


request_queue = None # RequestQueue


class RequestQueue:
    def __init__(self, config):
        self.queues = {}
        self.urls = {}
        self.is_running = {}

        for url in config:
            self.queues[url["name"]] = queue.Queue(maxsize=url["max_queue_size"])
            self.urls[url["name"]] = url["url"]
            self.is_running[url["name"]] = False

    def add_request(self, url_name, data, logger, extensions=None, method="POST"):
        timezone_name = "Asia/Shanghai"
        current_time = datetime.now(pytz.timezone(timezone_name))

        request_info = {
            "model": url_name,
            "url": self.urls[url_name],
            "method": method,
            "time": current_time,
            "timezone": timezone_name,
            "data": data,
            "logger": logger,
            "extensions": extensions,
        }

        try:
            self.queues[url_name].put(request_info, block=False)
            id = logger.get_prompt_id()
            threading.Thread(target=self.run, args=(url_name,)).start()
            return True, id
        except queue.Full:
            return False, "System is busy"

    def process_request(self, request_info):
        url = request_info['url']
        method = request_info['method']
        data = request_info['data']

        # Log request meta data
        logger = request_info['logger']
        print("log request meta data")
        logger.log_request(request_info)

        response = None

        if method == "POST":
            try:
                response = requests.post(url=url, json=data, timeout=600)
            except Exception:
                response = None
        else:
            print("method not supported")

        if response is None:
            print("response is None")
            return

        # Log response
        logger.log_response(response.json())

        # Execute extensions
        self.execute_extensions(request_info['extensions'], "post_request")

        return

    def is_empty(self, url_name):
        return self.queues[url_name].empty()

    def run(self, url_name):
        if self.is_running[url_name]:
            return
        self.is_running[url_name] = True
        while not self.is_empty(url_name):
            request_info = self.queues[url_name].get()
            self.process_request(request_info)
        self.is_running[url_name] = False

    def execute_extensions(self, extensions, trigger_time):
        extensions_ = [ext for ext in extensions if ext.trigger_time == trigger_time]
        extensions_ = sorted(extensions_)
        for ext in extensions_:
            ext.execute()


def initialize_request_queue(config):
    global request_queue
    request_queue = RequestQueue(config)


def add_request(url_name, data, logger, extensions=None):
    global request_queue
    state, description = request_queue.add_request(url_name, data, logger, extensions)
    return state, description
