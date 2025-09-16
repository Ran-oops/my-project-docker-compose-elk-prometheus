import logging
from logging.config import dictConfig
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
import redis
import psycopg2

# --- 导入所有需要的模块 ---
from asgi_correlation_id import CorrelationIdMiddleware
from .middlewares import LogAndMonitorMiddleware # 导入我们自己的中间件类
from prometheus_fastapi_instrumentator import Instrumentator # 导入 Instrumentator

from .dependencies import get_redis, get_db
from .kafka_producer import send_message
from .logging_config import LOGGING

# 在应用启动前应用日志配置
dictConfig(LOGGING)

# 获取一个 logger 实例
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
# --- 核心改动：在 Lifespan 外部完成所有定义和注册 ---
# --------------------------------------------------------------------

# 1. 定义 Lifespan 函数
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 应用启动时执行的代码现在可以保持简洁
    logger.info("FastAPI application startup complete.")
    yield
    # 应用关闭时执行的代码
    logger.info("FastAPI application shutting down.")

# 2. 创建 FastAPI 应用实例，并传入 lifespan
app = FastAPI(lifespan=lifespan)

# 3. 注册我们自己的中间件 (顺序很重要)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(LogAndMonitorMiddleware)

# 4. 应用并暴露自动化的 Instrumentator
#    这个操作也必须在 lifespan 开始之前完成
Instrumentator().instrument(app).expose(app)

# --------------------------------------------------------------------
# --- 端点代码保持不变 ---
# --------------------------------------------------------------------

@app.get("/")
def read_root():
    logger.info("Executing root endpoint logic.")
    return {"Hello": "World"}


@app.get("/health")
def health_check(redis_client: redis.Redis = Depends(get_redis), db_conn = Depends(get_db)):
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