# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Rumble URLs
    RUMBLE_REGISTER_URL = "https://auth.rumble.com/signup?theme=s&redirect_uri=https%3A%2F%2Frumble.com%2Fregister.html&lang=en_US"
    RUMBLE_LOGIN_URL = "https://rumble.com/login.html"
    
    # Browser settings
    HEADLESS_MODE = False
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Timing settings
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 30
    
    # Retry settings
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    # Output settings
    SAVE_LOGS = True
    SAVE_SCREENSHOTS = True
    
    # CAPTCHA Solver Settings
    # Local API (http://localhost:5000)
    LOCAL_CAPTCHA_API_KEY = os.getenv("LOCAL_CAPTCHA_API_KEY", "YOUR_KEY559d1b2771bedd55455c09865b97be55e04a0a9877978")
    
    # NextCaptcha API
    NEXTCAPTCHA_CLIENT_KEY = os.getenv("NEXTCAPTCHA_CLIENT_KEY", "f7a39c56d0714ab6856e9c85c1fb47e5")

config = Config()