"""`realtime_asgi(app)`: WebSocket scopes on `RealtimeConfig.path` go to the realtime handler, the rest to `app`.

    # api/asgi.py
    application = realtime_asgi(get_asgi_application())

Lifespan is answered here (Django's ASGI handler refuses non-http scopes). On SIGTERM uvicorn itself closes every
open socket with 1012 before it runs the lifespan shutdown; the shutdown here closes whatever is left with 1012 too.
A websocket scope on another path, or with realtime disabled, is refused before it is accepted: the app sends
`websocket.close` (code 1008), which uvicorn turns into an HTTP 403 response to the handshake.
"""

from __future__ import annotations

import logging

from .protocol import Close

logger = logging.getLogger(__name__)


class RealtimeRouter:
    def __init__(self, app, *, hooks=None) -> None:
        self.app = app
        self.hooks = hooks  # None: the default HookRunner (tests may inject InlineHookRunner)

    async def __call__(self, scope, receive, send) -> None:
        kind = scope["type"]
        if kind == "websocket":
            await self._websocket(scope, receive, send)
        elif kind == "lifespan":
            await self._lifespan(receive, send)
        else:
            await self.app(scope, receive, send)

    async def _websocket(self, scope, receive, send) -> None:
        from .backends import get_realtime_config

        config = get_realtime_config()
        path = (scope.get("path") or "/").rstrip("/") or "/"
        if not config.enabled or path != config.path:
            message = await receive()
            if message.get("type") == "websocket.connect":
                await send({"type": "websocket.close", "code": 1008})
            return
        from .connection import Connection
        from .hub import get_hub

        await Connection(scope, receive, send, hub=get_hub(), config=config, hooks=self.hooks).run()

    async def _lifespan(self, receive, send) -> None:
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                from .hub import shutdown_hubs

                try:
                    await shutdown_hubs(Close.RESTART)
                except Exception as exc:  # noqa: BLE001 - shutdown must complete
                    logger.warning("realtime: shutdown closed sockets with an error: %s", exc)
                await send({"type": "lifespan.shutdown.complete"})
                return


def realtime_asgi(app, *, hooks=None) -> RealtimeRouter:
    """Wrap a Django ASGI application with the realtime WebSocket endpoint.

    `hooks` replaces the hook runner of every connection (tests: `connection.InlineHookRunner()`).
    """
    return RealtimeRouter(app, hooks=hooks)


__all__ = ["RealtimeRouter", "realtime_asgi"]
