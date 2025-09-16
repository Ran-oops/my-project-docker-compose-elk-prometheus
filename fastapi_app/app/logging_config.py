import os
import logging
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
import requests
from pythonjsonlogger import jsonlogger # <--- 直接导入 formatter 类

LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "logstash")
LOGSTASH_PORT = int(os.getenv("LOGSTASH_PORT", 8099))
LOGSTASH_URL = f"http://{LOGSTASH_HOST}:{LOGSTASH_PORT}/"

# 自定义一个 HTTP Handler
class JsonHTTPHandler(logging.Handler):
    def __init__(self, url, method='POST'):
        super().__init__()
        self.url = url
        self.method = method

    def emit(self, record):
        log_entry = self.format(record)
        try:
            requests.request(
                self.method,
                self.url,
                data=log_entry,
                headers={"Content-type": "application/json"},
                timeout=1
            )
        except requests.RequestException:
            pass

# --- 核心改动：简化异步处理的设置 ---

# 1. 直接创建我们需要的 json formatter 实例
json_formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")

# 2. 创建我们的 HTTP handler 实例
http_handler = JsonHTTPHandler(url=LOGSTASH_URL)
# 3. 将 formatter 应用到 handler
http_handler.setFormatter(json_formatter)

# 4. 创建日志队列和监听器，让它使用我们配置好的 handler
log_queue = Queue(-1)
queue_listener = QueueListener(log_queue, http_handler)
queue_listener.start()

# 5. 定义最终的 LOGGING 字典
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # 我们仍然可以为 console 定义一个简单的 formatter
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        # 这个 handler 只是一个队列入口
        "queue": {
            "class": "logging.handlers.QueueHandler",
            "queue": log_queue,
        },
    },
    "root": {
        # 所有日志都发往 console 和 queue
        "handlers": ["console", "queue"],
        "level": "INFO",
    },
    "loggers": {
        "uvicorn.error": {"handlers": ["console", "queue"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["console", "queue"], "level": "INFO", "propagate": False},
    },
}