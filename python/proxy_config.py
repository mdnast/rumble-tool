"""
Proxy configuration file
Add your proxies here in the format: protocol://user:pass@host:port
"""

PROXY_LIST = [
    # Example formats:
    # "http://username:password@proxy.example.com:8080",
    # "http://proxy.example.com:8080",  # No auth
    # "socks5://username:password@proxy.example.com:1080",
]

# Set to True to rotate proxies randomly
USE_PROXY_ROTATION = False

# Set to True to use a single proxy
USE_SINGLE_PROXY = False
SINGLE_PROXY = None  # Set your proxy here if USE_SINGLE_PROXY is True

def get_proxy():
    """Get a proxy from the list"""
    if USE_SINGLE_PROXY and SINGLE_PROXY:
        return SINGLE_PROXY
    
    if USE_PROXY_ROTATION and PROXY_LIST:
        import random
        return random.choice(PROXY_LIST)
    
    return None
