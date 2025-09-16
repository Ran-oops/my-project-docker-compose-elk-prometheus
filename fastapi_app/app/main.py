import logging
from logging.config import dictConfig
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
import redis
import psycopg2

# --- 导入所有需要的模块 ---
from asgi_correlation_id import CorrelationIdMiddleware
from .middlewares import log_and_monitor_middleware
from prometheus_fastapi_instrumentator import Instrumentator

from .dependencies import get_redis, get_db
from .kafka_producer import send_message
from .logging_config import LOGGING

# 在应用启动前应用日志配置
dictConfig(LOGGING)

# 获取一个 logger 实例
logger = logging.getLogger(__name__)


# --- 这是核心改动：使用 lifespan 上下文管理器 ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行的代码

    # 1. 创建并应用 Instrumentator
    instrumentator = Instrumentator().instrument(app)

    # 2. 暴露 /metrics 端点
    instrumentator.expose(app)

    logger.info("FastAPI application startup complete. Metrics exposed.")

    yield

    # 应用关闭时执行的代码 (如果需要)
    logger.info("FastAPI application shutting down.")


# 将 lifespan 函数传递给 FastAPI
app = FastAPI(lifespan=lifespan)

# --- 注册中间件 (顺序很重要) ---
# a. 添加 CorrelationIdMiddleware，它必须在最前面
app.add_middleware(CorrelationIdMiddleware)
# b. 添加我们自己编写的日志和自定义指标中间件
app.add_middleware(log_and_monitor_middleware)


# --- 端点代码保持不变 ---

@app.get("/")
def read_root():
    logger.info("Executing root endpoint logic.")
    return {"Hello": "World"}


@app.get("/health")
def health_check(redis_client: redis.Redis = Depends(get_redis), db_conn=Depends(get_db)):
    try:
        redis_client.ping()
        logger.debug("Redis connection is healthy.")
        db_conn.cursor().execute("SELECT 1")
        logger.debug("PostgreSQL connection is healthy.")
        if db_conn:
            db_conn.close()
        logger.info("Health check performed successfully.")
        return {"redis": "ok", "postgres": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {"status": "error", "details": str(e)}, 503


@app.post("/send_event")
async def send_event(message: dict):
    topic = "my-topic"
    logger.info(f"Received request to send a message to Kafka topic '{topic}'.")
    await send_message(topic, message)
    logger.info(f"Successfully sent message to Kafka topic '{topic}'.")
    return {"status": "message sent"}