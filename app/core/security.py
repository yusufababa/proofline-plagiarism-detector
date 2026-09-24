from __future__ import annotations

import base64
import binascii
import secrets
from collections.abc import Iterable

from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class BasicAccessMiddleware:
    """Protect hosted deployments when an access password is configured."""

    def __init__(
        self,
        app: ASGIApp,
        username: str,
        password: str,
        excluded_paths: Iterable[str] = (),
    ) -> None:
        self.app = app
        self.username = username
        self.password = password
        self.excluded_paths = frozenset(excluded_paths)

    def _is_authorized(self, scope: Scope) -> bool:
        authorization = next(
            (
                value.decode("latin-1")
                for name, value in scope.get("headers", ())
                if name.lower() == b"authorization"
            ),
            "",
        )
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() != "basic" or not credentials:
            return False
        try:
            decoded = base64.b64decode(credentials, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError):
            return False
        supplied_username, separator, supplied_password = decoded.partition(":")
        if not separator:
            return False
        return secrets.compare_digest(supplied_username, self.username) and secrets.compare_digest(
            supplied_password, self.password
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or not self.password
            or scope.get("path", "") in self.excluded_paths
            or self._is_authorized(scope)
        ):
            await self.app(scope, receive, send)
            return

        response = PlainTextResponse(
            "Authentication is required to use this Proofline deployment.",
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="Proofline", charset="UTF-8"'},
        )
        await response(scope, receive, send)
