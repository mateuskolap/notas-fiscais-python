import contextvars
from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    'request_id', default=''
)


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in {'http', 'websocket'}:
            await self.app(scope, receive, send)
            return

        request_id = ''
        headers = scope.get('headers', [])
        for name, value in headers:
            if name.lower() == b'x-request-id':
                try:
                    request_id = value.decode('utf-8')
                except UnicodeDecodeError:
                    pass
                break

        if not request_id:
            request_id = str(uuid4())

        token = request_id_ctx.set(request_id)

        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                msg_headers = list(message.get('headers', []))

                has_request_id = False
                for name, _ in msg_headers:
                    if name.lower() == b'x-request-id':
                        has_request_id = True
                        break

                if not has_request_id:
                    msg_headers.append((b'x-request-id', request_id.encode('utf-8')))
                    message['headers'] = msg_headers
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            request_id_ctx.reset(token)
