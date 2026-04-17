"""
Rate Limiter Module

Uses Redis if available, otherwise in-memory.
Sliding window algorithm.
"""
import time
from collections import defaultdict, deque
from fastapi import HTTPException

from app.config import settings

try:
    import redis
    r = redis.from_url(settings.redis_url) if settings.redis_url else None
except ImportError:
    r = None


class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        if r:
            self._redis = r
        else:
            self._windows: dict[str, deque] = defaultdict(deque)

    def check(self, user_id: str) -> dict:
        """
        Check if user is within rate limit.
        Raise 429 if exceeded.
        Returns dict with remaining info.
        """
        now = time.time()

        if r:
            # Redis-based
            key = f"ratelimit:{user_id}"
            # Remove old entries
            r.zremrangebyscore(key, 0, now - self.window_seconds)
            # Count current requests
            count = r.zcard(key)
            if count >= self.max_requests:
                oldest = r.zrange(key, 0, 0, withscores=True)
                if oldest:
                    retry_after = int(oldest[0][1] + self.window_seconds - now) + 1
                else:
                    retry_after = self.window_seconds
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(retry_after)},
                )
            # Add new request
            r.zadd(key, {str(now): now})
            r.expire(key, self.window_seconds)
            remaining = self.max_requests - count - 1
        else:
            # In-memory
            window = self._windows[user_id]
            while window and window[0] < now - self.window_seconds:
                window.popleft()
            if len(window) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": "60"},
                )
            window.append(now)
            remaining = self.max_requests - len(window)

        return {
            "limit": self.max_requests,
            "remaining": remaining,
            "reset_at": int(now) + self.window_seconds,
        }


# Global instance
rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_per_minute,
    window_seconds=60
)