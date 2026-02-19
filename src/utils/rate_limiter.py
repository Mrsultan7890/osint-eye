import time
import os
from functools import wraps

class RateLimiter:
    def __init__(self, delay=None):
        self.delay = delay or float(os.getenv("RATE_LIMIT_DELAY", "2"))
        self.last_call = 0
    
    def wait(self):
        """Wait if necessary to respect rate limit"""
        elapsed = time.time() - self.last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_call = time.time()

def rate_limit(delay=None):
    """Decorator to rate limit function calls"""
    limiter = RateLimiter(delay)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait()
            return func(*args, **kwargs)
        return wrapper
    return decorator