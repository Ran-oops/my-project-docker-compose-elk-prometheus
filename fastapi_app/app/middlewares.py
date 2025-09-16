# app/middlewares.py (最终修复版)

import time
import logging
from fastapi import Request
from asgi_correlation_id.context import correlation_id
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match

# --- Prometheus 指标定义 (保持不变) ---
API_REQUESTS = Counter(
    'myapp_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'http_status']
)

RESPONSE_TIME = Histogram(
    'http_response_time_seconds',
    'HTTP response time in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1, 2, 5]
)


# --- 核心改动：将中间件逻辑包装成一个类 ---
class LogAndMonitorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # --- 日志上下文增强 ---
        request_id = correlation_id.get()
        logger = logging.getLogger(__name__)

        extra_context = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
        }
        adapter = logging.LoggerAdapter(logger, extra_context)

        start_time = time.time()
        adapter.info("Request started", extra={"event": "request_started"})

        # --- 处理请求 ---
        response = await call_next(request)

        # --- 记录指标和日志 ---
        process_time = time.time() - start_time
        status_code = response.status_code

        # 尝试从路由中获取规范化的端点路径，而不是原始路径
        endpoint = request.url.path
        for route in request.app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                endpoint = route.path
                break

        adapter.info(
            "Request finished",
            extra={
                "event": "request_finished",
                "status_code": status_code,
                "process_time_ms": round(process_time * 1000, 2)
            }
        )

        RESPONSE_TIME.labels(method=request.method, endpoint=endpoint).observe(process_time)
        API_REQUESTS.labels(method=request.method, endpoint=endpoint, http_status=status_code).inc()

        return response