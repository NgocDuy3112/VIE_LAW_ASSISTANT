from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config import RATE_LIMIT_URI


# Always create the limiter instance at module level
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=RATE_LIMIT_URI
)

async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )

def setup_rate_limit(app: FastAPI):
    # Attach limiter to app state
    app.state.limiter = limiter

    # Register exception handler
    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

    # Optionally: add ASGI middleware so it works globally
    # app.add_middleware(SlowAPIMiddleware)