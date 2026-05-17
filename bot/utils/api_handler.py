import logging
import time
from typing import Any, Dict, Optional, Union

import requests

log = logging.getLogger(__name__)

class APIHandler:
    """Centralized API handler with retry logic and exponential backoff."""
    
    def __init__(self, max_retries: int = 3, initial_backoff: float = 1.0, max_backoff: float = 60.0):
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
    
    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make an HTTP request with retry logic and exponential backoff."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    log.error(f"API request failed after {self.max_retries} retries: {url}")
                    raise
                
                # Calculate backoff time with exponential jitter
                backoff = min(self.initial_backoff * (2 ** attempt), self.max_backoff)
                jitter = backoff * 0.2  # Add up to 20% jitter
                sleep_time = backoff + jitter
                
                log.warning(f"API request failed (attempt {attempt + 1}/{self.max_retries}): {url}. Retrying in {sleep_time:.2f}s...")
                time.sleep(sleep_time)
        
        if last_exception:
            raise last_exception
        
        # This should never be reached, but just in case
        raise Exception(f"API request failed after {self.max_retries} retries: {url}")
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Make a GET request."""
        return self.request("GET", url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make a POST request."""
        return self.request("POST", url, **kwargs)
    
    def put(self, url: str, **kwargs) -> requests.Response:
        """Make a PUT request."""
        return self.request("PUT", url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> requests.Response:
        """Make a DELETE request."""
        return self.request("DELETE", url, **kwargs)