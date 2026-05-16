# Earning modules
from .twitter import run as twitter_run

# Fallback for missing anthropic module
def anthropic_run(*args, **kwargs):
    pass