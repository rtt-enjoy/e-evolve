import logging
import time
from typing import Dict, Optional

log = logging.getLogger(__name__)

class RateLimiter:
    """Tracks API usage per provider and warns when approaching limits."""
    
    def __init__(self, warning_threshold: float = 0.8, reset_interval: int = 60):
        self.warning_threshold = warning_threshold
        self.reset_interval = reset_interval  # seconds
        self.usage: Dict[str, Dict[str, float]] = {}
        self.last_reset = time.time()
    
    def record_usage(self, provider: str, endpoint: str, amount: float = 1.0) -> None:
        """Record API usage for a specific provider and endpoint."""
        current_time = time.time()
        
        # Reset usage counters if interval has passed
        if current_time - self.last_reset > self.reset_interval:
            self.usage = {}
            self.last_reset = current_time
        
        if provider not in self.usage:
            self.usage[provider] = {}
        
        if endpoint not in self.usage[provider]:
            self.usage[provider][endpoint] = 0.0
        
        self.usage[provider][endpoint] += amount
        
        # Check if we're approaching the limit
        total_usage = sum(self.usage[provider].values())
        if total_usage >= self.warning_threshold:
            log.warning(f"API usage warning for {provider}: {total_usage:.2f} calls in the last {self.reset_interval}s")
    
    def get_usage(self, provider: str, endpoint: Optional[str] = None) -> float:
        """Get current usage for a provider or specific endpoint."""
        if provider not in self.usage:
            return 0.0
        
        if endpoint is None:
            return sum(self.usage[provider].values())
        
        return self.usage[provider].get(endpoint, 0.0)
    
    def is_limited(self, provider: str, endpoint: Optional[str] = None) -> bool:
        """Check if usage has exceeded the warning threshold."""
        return self.get_usage(provider, endpoint) >= self.warning_threshold