# fastapi_app/app/main.py

import logging
from logging.config import dictConfig
from fastapi import FastAPI, Depends, Request
from prometheus_fastapi_instrumentator import Instrumentator
import redis
import psycopg2
from .dependencies import get_redis, get_db
from .kafka_producer import send_message
from .logging_config import LOGGING # <--- 导入日志配置

# 在应用启动前应用日志配置
dictConfig(LOGGING)

# 获取一个 logger 实例
logger = logging.getLogger(__name__)

app = FastAPI()

# 暴露 Prometheus 指标
Instrumentator().instrument(app).expose(app)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request started: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Request finished: {request.method} {request.url.path} with status {response.status_code}")
    return response

@app.get("/")
def read_root():
    logger.info("Accessing the root endpoint.")
    return {"Hello": "World"}

@app.get("/health")
def health_check(redis_client: redis.Redis = Depends(get_redis), db_conn = Depends(get_db)):
    # ... (原有代码保持不变) ...
    logger.info("Health check performed.")
    return {"redis": "ok", "postgres": "ok"}


@app.post("/send_event")
async def send_event(message: dict):
    topic = "my-topic"
    logger.info(f"Received request to send a message to Kafka topic '{topic}'.", extra={"kafka_topic": topic, "message_body": message})
    await send_message(topic, message)
    logger.info(f"Successfully sent message to Kafka topic '{topic}'.")
    return {"status": "message sent"}