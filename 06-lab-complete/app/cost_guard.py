"""
Cost Guard Module

Tracks monthly spending per user.
Uses Redis for persistence.
"""
import time
from datetime import datetime
from fastapi import HTTPException

from app.config import settings

try:
    import redis
    r = redis.from_url(settings.redis_url) if settings.redis_url else None
except ImportError:
    r = None


class CostGuard:
    def __init__(self, monthly_budget_usd: float = 10.0):
        self.monthly_budget_usd = monthly_budget_usd
        self._global_cost = 0.0

    def check_budget(self, user_id: str, estimated_cost: float) -> bool:
        """
        Check if user has budget for estimated cost.
        Raise 402 if exceeded.
        """
        month_key = datetime.now().strftime("%Y-%m")
        key = f"budget:{user_id}:{month_key}"

        if r:
            current = float(r.get(key) or 0)
        else:
            # In-memory fallback (resets on restart)
            current = getattr(self, f"_budget_{user_id}", 0.0)

        if current + estimated_cost > self.monthly_budget_usd:
            raise HTTPException(
                status_code=402,
                detail="Monthly budget exceeded",
            )
        return True

    def record_usage(self, user_id: str, input_tokens: int, output_tokens: int) -> dict:
        """
        Record actual usage and return cost info.
        """
        # Simple cost calculation (adjust for real LLM pricing)
        cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006

        month_key = datetime.now().strftime("%Y-%m")
        key = f"budget:{user_id}:{month_key}"

        if r:
            r.incrbyfloat(key, cost)
            r.expire(key, 32 * 24 * 3600)  # 32 days
            current = float(r.get(key) or 0)
        else:
            current = getattr(self, f"_budget_{user_id}", 0.0) + cost
            setattr(self, f"_budget_{user_id}", current)

        self._global_cost += cost

        return {
            "cost_usd": round(cost, 4),
            "total_cost_usd": round(current, 4),
            "budget_usd": self.monthly_budget_usd,
            "remaining_usd": round(self.monthly_budget_usd - current, 4),
        }

    def get_usage(self, user_id: str) -> dict:
        """Get current usage for user."""
        month_key = datetime.now().strftime("%Y-%m")
        key = f"budget:{user_id}:{month_key}"

        if r:
            current = float(r.get(key) or 0)
        else:
            current = getattr(self, f"_budget_{user_id}", 0.0)

        return {
            "monthly_spending_usd": round(current, 4),
            "monthly_budget_usd": self.monthly_budget_usd,
            "remaining_usd": round(self.monthly_budget_usd - current, 4),
        }


# Global instance
cost_guard = CostGuard(monthly_budget_usd=10.0)