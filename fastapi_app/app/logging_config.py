import os

LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "logstash")
# Logstash HTTP input 默认端口是 8080，但为了避免冲突，我们用一个自定义端口
LOGSTASH_PORT = int(os.getenv("LOGSTASH_PORT", 8099))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "logstash": { # 这个 formatter 保持不变
            "()": "logstash_async.formatter.LogstashFormatter",
            "message_type": "python-logstash",
            "extra": {"application": "my-fastapi-app"}
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        # --- 修改 logstash handler ---
        "logstash": {
            # 更换为 HTTP Handler
            "class": "logstash_async.handler.AsynchronousLogstashHandler",
            "formatter": "logstash",
            "host": LOGSTASH_HOST,
            "port": LOGSTASH_PORT,
            "database_path": "logstash_events.db",
            # --- 添加这两行来启用 SSL 和 HTTP ---
            "ssl_enable": False, # 在 Docker 内部网络，我们不需要 SSL
            "use_logging_http_handler": True,
        },
    },
    "root": {
        "handlers": ["console", "logstash"],
        "level": "INFO",
    },
    "loggers": { # loggers 部分保持不变
        "uvicorn.error": {"handlers": ["console", "logstash"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["console", "logstash"], "level": "INFO", "propagate": False},
    },
}