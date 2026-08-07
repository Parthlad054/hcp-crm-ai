"""
limiter.py — Shared slowapi rate-limiter instance.

Import `limiter` into any router that needs @limiter.limit(...).
The app must register it via:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Key function: rate-limit by the caller's IP address.
# For production behind a trusted proxy, replace with a function that reads
# the X-Forwarded-For header after validating the proxy.
limiter = Limiter(key_func=get_remote_address)
