import time
from app.db import redis_client

RATE_LIMIT_MAX_REQUESTS = 20   # max requests allowed
RATE_LIMIT_WINDOW_SECONDS = 60  # per this many seconds


async def is_rate_limited(identifier: str) -> bool:
    """
    Sliding-window rate limiter using a Redis sorted set.
    'identifier' is typically the user_id or client IP.
    Returns True if the request should be blocked.
    """
    key = f"rate_limit:{identifier}"
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS

    try:
        pipe = redis_client.pipeline()
        # Remove requests older than the window
        pipe.zremrangebyscore(key, 0, window_start)
        # Count requests within the window
        pipe.zcard(key)
        # Add this request
        pipe.zadd(key, {str(now): now})
        # Expire the whole key after the window passes, so it cleans itself up
        pipe.expire(key, RATE_LIMIT_WINDOW_SECONDS)
        results = await pipe.execute()

        request_count = results[1]
        return request_count >= RATE_LIMIT_MAX_REQUESTS

    except Exception:
        # If Redis is down, fail open (don't block legitimate traffic) —
        # rate limiting is a protection layer, not core fraud logic.
        return False