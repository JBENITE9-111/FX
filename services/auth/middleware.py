from __future__ import annotations

from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from services.auth.session import COOKIE_NAME, verify_session
from services.auth.totp import totp_service


class TotpAccessMiddleware(BaseHTTPMiddleware):
    PUBLIC_PATHS = {
        "/health",
        "/security",
        "/api/security/totp/status",
        "/api/security/totp/enroll",
        "/api/security/totp/confirm",
        "/api/security/totp/login",
        "/api/security/totp/logout",
        "/api/security/sentinel",
    }

    async def dispatch(self, request, call_next):
        path = request.url.path.rstrip("/") or "/"
        if (
            not totp_service.is_enrolled()
            or path in self.PUBLIC_PATHS
            or verify_session(request.cookies.get(COOKIE_NAME))
        ):
            response = await call_next(request)
        elif path.startswith("/api/"):
            response = JSONResponse(
                {"ok": False, "message": "Two-factor authentication is required.", "unlock_url": "/security"},
                status_code=401,
            )
        else:
            response = RedirectResponse("/security", status_code=303)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response
