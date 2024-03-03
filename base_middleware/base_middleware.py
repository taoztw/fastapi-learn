from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request
from starlette.responses import Response
import contextvars
import uuid
request_context = contextvars.ContextVar("request_content")

class AuthMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, header_value):
        super().__init__(app)
        self.header_value = header_value

    # dispatch方法必须实现
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers["Custom"] = self.header_value
        return response


class TracedIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_context.set(request)
        request.state.traceid = uuid.uuid4()
        response = await call_next(request)
        return response