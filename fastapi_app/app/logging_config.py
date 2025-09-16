# fastapi_app/app/logging_config.py
import os

LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "logstash")
LOGSTASH_PORT = int(os.getenv("LOGSTASH_PORT", 50000)) # Logstash TCP input 端口

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # 这个 formatter 用于在控制台（stdout）输出，方便本地调试
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        # 这个 formatter 用于发送到 Logstash，可以添加额外字段
        "logstash": {
            "()": "logstash_async.formatter.LogstashFormatter",
            "message_type": "python-logstash",
            "extra_prefix": "dev",
            "extra": {
                "application": "my-fastapi-app"
            }
        },
    },
    "handlers": {
        # 控制台输出 handler
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        # Logstash TCP handler
        "logstash": {
            "class": "logstash_async.handler.AsynchronousLogstashHandler",
            "formatter": "logstash",
            "host": LOGSTASH_HOST,
            "port": LOGSTASH_PORT,
            "database_path": "logstash_events.db", # 离线缓冲数据库路径
        },
    },
    # 配置根 logger，让它同时使用 console 和 logstash
    "root": {
        "handlers": ["console", "logstash"],
        "level": "INFO",
    },
    "loggers": {
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console", "logstash"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console", "logstash"],
            "propagate": False,
        },
    },
}