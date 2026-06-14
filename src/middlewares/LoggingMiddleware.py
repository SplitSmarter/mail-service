import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.config.config import TRACE_ID_HEADER_NAME, USER_ID_HEADER_NAME, get_logger, MAX_BODY_LOG_LENGTH


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get(TRACE_ID_HEADER_NAME, str(uuid.uuid4()))
        user_id = request.headers.get(USER_ID_HEADER_NAME, None)
        request.state.trace_id = trace_id

        body_bytes = await request.body()
        try:
            body_str = body_bytes.decode("utf-8")
        except UnicodeDecodeError:
            body_str = str(body_bytes)

        if len(body_str) > MAX_BODY_LOG_LENGTH:
            body_str = body_str[:MAX_BODY_LOG_LENGTH] + "...(truncated)"

        logger = get_logger(trace_id)

        logger.info(
            f"  Incoming request: {request.method} {request.url.path} "
            f"query={dict(request.query_params)} "
            f"user={user_id} "
            f"client={request.client.host if request.client else 'unknown'} "
            f"user-agent={request.headers.get('user-agent')} "
            f"body={body_str}"
        )

        start_time = time.time()
        try:
            response = await call_next(request)
        except Exception as e:
            logger.exception(f"Unhandled error: {e}")
            raise

        duration = (time.time() - start_time) * 1000
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"status_code={response.status_code} "
            f"duration={duration:.2f}ms"
        )

        response.headers[TRACE_ID_HEADER_NAME] = trace_id
        return response
