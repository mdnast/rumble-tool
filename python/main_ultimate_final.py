"""
RUMBLE ULTIMATE BYPASS - FINAL VERSION
Kết hợp TẤT CẢ kỹ thuật bypass bot detection:
- Undetected ChromeDriver
- Stealth JavaScript injection
- Human behavior simulation
- CAPTCHA solver (Local + NextCaptcha)
- Canvas/WebGL/Audio fingerprint spoofing
"""

import time
import logging
import os
import random
import string
import json
from datetime import datetime, timedelta

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import CAPTCHA solver
try:
    from captcha_solver import CaptchaSolver
    from config import Config
    HAS_CAPTCHA_SOLVER = True
except:
    HAS_CAPTCHA_SOLVER = False
    print("[WARN] CAPTCHA solver not available")

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rumble_ultimate_final.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# STEALTH SCRIPTS - Inject to bypass detection
STEALTH_SCRIPTS = {
    'webdriver': """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """,
    
    'chrome': """
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
    """,
    
    'permissions': """
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """,
    
    'plugins': """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: ''},
                {name: 'Native Client', filename: 'internal-nacl-plugin', description: ''}
            ]
        });
    """,
    
    'languages': """
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """,
    
    'canvas': """
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {
            if (type === 'image/png' && this.width === 280 && this.height === 60) {
                return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
            }
            return originalToDataURL.apply(this, arguments);
        };
    """,
    
    'webgl': """
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter.apply(this, arguments);
        };
    """,
    
    'battery': """
        Object.defineProperty(navigator, 'getBattery', {
            get: () => async () => ({
                charging: true,
                chargingTime: 0,
                dischargingTime: Infinity,
                level: 1.0
            })
        });
    """,
    
    'connection': """
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 50,
                downlink: 10,
                saveData: false
            })
        });
    """,
    
    'deviceMemory': """
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
    """,
    
    'hardwareConcurrency': """
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
    """
}

class RumbleUltimateBypass:
    def __init__(self, use_proxy=None, email_file=None):
        """
        Initialize Ultimate Bypass
        Args:
            use_proxy: Proxy string (e.g., "http://user:pass@host:port")
            email_file: Path to file containing emails (one per line)
        """
        self.driver = None
        self.captcha_solver = None
        self.use_proxy = use_proxy
        self.email_file = email_file
        self.emails = []
        self.current_email_index = 0
        
        # Load emails from file if provided
        if self.email_file and os.path.exists(self.email_file):
            try:
                with open(self.email_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and '@' in line:
                            # Support format: email:password or just email
                            if ':' in line:
                                email = line.split(':')[0].strip()
                            else:
                                email = line
                            self.emails.append(email)
                logger.info(f"[EMAIL] Loaded {len(self.emails)} emails from file")
            except Exception as e:
                logger.error(f"[EMAIL] Failed to load file: {e}")
                self.emails = []
        
        # Initialize CAPTCHA solver
        if HAS_CAPTCHA_SOLVER:
            try:
                self.captcha_solver = CaptchaSolver(
                    local_api_key=Config.LOCAL_CAPTCHA_API_KEY,
                    nextcaptcha_client_key=Config.NEXTCAPTCHA_CLIENT_KEY,
                    yescaptcha_client_key=Config.YESCAPTCHA_CLIENT_KEY
                )
                logger.info("[CAPTCHA] Solver initialized with YesCaptcha")
            except Exception as e:
                logger.warning(f"[CAPTCHA] Could not initialize: {e}")
        
        self.setup_driver()
    
    def setup_driver(self):
        """Setup undetected Chrome with MAXIMUM stealth options"""
        try:
            logger.info("[DRIVER] Initializing MAXIMUM stealth Chrome...")
            
            options = uc.ChromeOptions()
            
            # Maximum anti-detection flags (safe ones)
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            options.add_argument('--start-maximized')
            
            # More natural window size (common resolutions)
            common_sizes = [(1920, 1080), (1366, 768), (1440, 900), (1536, 864)]
            width, height = random.choice(common_sizes)
            options.add_argument(f'--window-size={width},{height}')
            
            # More realistic user agents (latest Chrome versions)
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Proxy
            if self.use_proxy:
                options.add_argument(f'--proxy-server={self.use_proxy}')
                logger.info(f"[PROXY] Using proxy: {self.use_proxy}")
            
            # Enhanced prefs to look more like real Chrome
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "profile.managed_default_content_settings.images": 1,
                "profile.default_content_setting_values.geolocation": 1,
                "profile.default_content_setting_values.media_stream": 1,
                "intl.accept_languages": "en-US,en;q=0.9",
            }
            options.add_experimental_option("prefs", prefs)
            # excludeSwitches not supported in undetected-chromedriver
            
            # Initialize driver
            self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
            
            # Critical: Wait after browser init before ANY action
            logger.info("[DRIVER] Browser opened, waiting for stabilization...")
            time.sleep(random.uniform(3, 5))
            
            # Inject stealth scripts
            self.inject_stealth_scripts()
            
            # Set implicit wait
            self.driver.implicitly_wait(10)
            
            # Visit a neutral page first (Google) to establish normal browser behavior
            try:
                logger.info("[DRIVER] Visiting Google first (look natural)...")
                self.driver.get("https://www.google.com")
                time.sleep(random.uniform(2, 4))
                
                # Scroll a bit on Google
                self.driver.execute_script("window.scrollTo(0, 100);")
                time.sleep(random.uniform(1, 2))
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(random.uniform(1, 2))
                
                logger.info("[DRIVER] Google visit complete")
            except Exception as e:
                logger.warning(f"[DRIVER] Google visit failed: {e}")
            
            logger.info("[DRIVER] ULTIMATE Chrome initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[DRIVER] Failed to initialize: {e}")
            return False
    
    def inject_stealth_scripts(self):
        """Inject all stealth JavaScript"""
        try:
            logger.info("[STEALTH] Injecting anti-detection scripts...")
            
            # Execute each stealth script
            for name, script in STEALTH_SCRIPTS.items():
                try:
                    self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                        'source': script
                    })
                    logger.info(f"[STEALTH] Injected: {name}")
                except Exception as e:
                    logger.warning(f"[STEALTH] Failed to inject {name}: {e}")
            
            logger.info("[STEALTH] All stealth scripts injected")
            
        except Exception as e:
            logger.warning(f"[STEALTH] Error injecting scripts: {e}")
    
    def human_delay(self, min_sec=0.5, max_sec=2.0):
        """Random human-like delay"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def human_type(self, element, text, make_mistakes=True):
        """Type text like a human with random delays and occasional mistakes"""
        element.clear()
        
        # Sometimes make a typo and correct it
        if make_mistakes and random.random() < 0.3:  # 30% chance
            # Type part of text
            mistake_at = random.randint(1, len(text) - 1)
            for i, char in enumerate(text[:mistake_at]):
                element.send_keys(char)
                time.sleep(random.uniform(0.08, 0.18))
            
            # Add wrong character
            wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
            element.send_keys(wrong_char)
            time.sleep(random.uniform(0.1, 0.3))
            
            # Pause (realize mistake)
            time.sleep(random.uniform(0.3, 0.7))
            
            # Delete wrong character
            from selenium.webdriver.common.keys import Keys
            element.send_keys(Keys.BACKSPACE)
            time.sleep(random.uniform(0.15, 0.35))
            
            # Continue typing correctly
            for char in text[mistake_at:]:
                element.send_keys(char)
                time.sleep(random.uniform(0.08, 0.18))
        else:
            # Normal typing with variable speed
            for i, char in enumerate(text):
                element.send_keys(char)
                # Vary typing speed (faster in middle, slower at start/end)
                if i < 3 or i > len(text) - 3:
                    time.sleep(random.uniform(0.10, 0.20))
                else:
                    time.sleep(random.uniform(0.05, 0.12))
        
        self.human_delay(0.4, 0.8)
    
    def human_mouse_move(self, element):
        """Move mouse to element in human-like way"""
        try:
            actions = ActionChains(self.driver)
            # Random movement
            actions.move_to_element_with_offset(element, 
                random.randint(-10, 10), 
                random.randint(-10, 10)
            )
            actions.perform()
            self.human_delay(0.2, 0.5)
        except:
            pass
    
    def get_next_email(self):
        """Get next email from file or generate random"""
        if self.emails and self.current_email_index < len(self.emails):
            email = self.emails[self.current_email_index]
            self.current_email_index += 1
            logger.info(f"[EMAIL] Using email from file ({self.current_email_index}/{len(self.emails)})")
            return email
        else:
            # Fallback to random generation
            random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
            email = f"{random_str}.{random.randint(1000, 9999)}@gmail.com"
            logger.info("[EMAIL] Generated random email")
            return email
    
    def generate_user_data(self):
        """Generate random user data"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
        
        # Random birthday (18-30 years old)
        years_ago = random.randint(18, 30)
        birth_date = datetime.now() - timedelta(days=years_ago * 365 + random.randint(0, 365))
        
        months = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        
        # Get email from file or generate
        email = self.get_next_email()
        
        return {
            'email': email,
            'username': f"{random_str}{random.randint(10, 99)}",
            'gender_value': random.choice(['male', 'female']),
            'birth_month_text': months[birth_date.month - 1],
            'birth_day': str(birth_date.day),
            'birth_year': str(birth_date.year)
        }
    
    def navigate_to_registration(self):
        """Navigate to registration page with human behavior"""
        try:
            url = "https://rumble.com/register/"
            logger.info(f"[NAV] Navigating to: {url}")
            
            self.driver.get(url)
            
            # Wait for page load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            logger.info("[NAV] Page loaded successfully")
            
            # Longer initial pause (crucial!)
            logger.info("[HUMAN] Initial page observation...")
            self.human_delay(3, 5)
            
            # Human behavior: multiple small scrolls to "read" page
            scroll_positions = [50, 120, 80, 150, 100, 0]
            for pos in scroll_positions:
                self.driver.execute_script(f"window.scrollTo({{top: {pos}, behavior: 'smooth'}});")
                self.human_delay(0.8, 1.5)
            
            # Final pause before starting
            self.human_delay(1.5, 2.5)
            
            return True
            
        except Exception as e:
            logger.error(f"[NAV] Failed: {e}")
            return False
    
    def detect_and_solve_captcha(self, timeout=120):
        """Detect and solve Cloudflare Turnstile (after form submit)"""
        if not self.captcha_solver:
            logger.info("[CAPTCHA] No solver configured")
            return True
        
        try:
            # Wait a bit for challenge to appear
            time.sleep(2)
            
            # Check for Turnstile iframes
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            turnstile_found = False
            
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                if "challenges.cloudflare.com" in src or "turnstile" in src.lower():
                    turnstile_found = True
                    logger.info(f"[CAPTCHA] Cloudflare Turnstile detected! URL: {src}")
                    break
            
            # Also check for Turnstile widget by class
            turnstile_widgets = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'cf-turnstile')]")
            if turnstile_widgets:
                turnstile_found = True
                logger.info("[CAPTCHA] Turnstile widget found by class")
            
            if not turnstile_found:
                logger.info("[CAPTCHA] No CAPTCHA detected")
                return True
            
            # Extract sitekey
            import re
            page_source = self.driver.page_source
            
            sitekey = None
            
            # Try multiple patterns
            patterns = [
                r'data-sitekey="([^"]+)"',
                r'sitekey:\s*["\']([^"\' ]+)["\']',
                r'"sitekey":\s*"([^"]+)"',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, page_source)
                if match:
                    sitekey = match.group(1)
                    logger.info(f"[CAPTCHA] Found sitekey with pattern: {pattern}")
                    break
            
            # Also check iframe src
            if not sitekey:
                for iframe in iframes:
                    src = iframe.get_attribute("src") or ""
                    match = re.search(r'sitekey=([^&\s]+)', src)
                    if match:
                        sitekey = match.group(1)
                        logger.info(f"[CAPTCHA] Found sitekey in iframe src")
                        break
            
            if not sitekey:
                logger.error("[CAPTCHA] Could not find sitekey")
                # Save page for debugging
                debug_file = os.path.join("logs", f"captcha_no_sitekey_{int(time.time())}.html")
                with open(debug_file, "w", encoding="utf-8") as f:
                    f.write(page_source)
                logger.info(f"[DEBUG] Page source saved to {debug_file}")
                return False
            
            logger.info(f"[CAPTCHA] Sitekey: {sitekey}")
            logger.info(f"[CAPTCHA] URL: {self.driver.current_url}")
            logger.info("[CAPTCHA] Solving with YesCaptcha API...")
            
            # Solve with API
            token = self.captcha_solver.solve_turnstile(
                self.driver.current_url, 
                sitekey, 
                timeout
            )
            
            if token:
                logger.info(f"[CAPTCHA] Token received: {token[:50]}...")
                logger.info("[CAPTCHA] Injecting token...")
                
                # Inject token (multiple methods)
                injection_script = f"""
                // Method 1: Fill existing cf-turnstile-response fields
                var textareas = document.querySelectorAll('textarea[name="cf-turnstile-response"]');
                console.log('[INJECT] Found ' + textareas.length + ' cf-turnstile-response textareas');
                for (var i = 0; i < textareas.length; i++) {{
                    textareas[i].value = '{token}';
                    textareas[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    textareas[i].dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
                
                // Method 2: Add hidden inputs to all forms
                var forms = document.querySelectorAll('form');
                console.log('[INJECT] Found ' + forms.length + ' forms');
                for (var i = 0; i < forms.length; i++) {{
                    var existingInput = forms[i].querySelector('input[name="cf-turnstile-response"]');
                    if (!existingInput) {{
                        var input = document.createElement('input');
                        input.type = 'hidden';
                        input.name = 'cf-turnstile-response';
                        input.value = '{token}';
                        forms[i].appendChild(input);
                        console.log('[INJECT] Added input to form ' + i);
                    }} else {{
                        existingInput.value = '{token}';
                        console.log('[INJECT] Updated existing input in form ' + i);
                    }}
                }}
                
                // Method 3: Try global Turnstile callback
                if (window.turnstile) {{
                    console.log('[INJECT] Turnstile object found');
                }}
                
                return 'Token injected successfully';
                """
                
                result = self.driver.execute_script(injection_script)
                logger.info(f"[CAPTCHA] Injection result: {result}")
                
                # Wait a bit for token to be processed
                self.human_delay(2, 3)
                
                logger.info("[CAPTCHA] Token injected successfully")
                return True
            else:
                logger.error("[CAPTCHA] Failed to get token from API")
                return False
            
        except Exception as e:
            logger.error(f"[CAPTCHA] Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def fill_form(self, user_data):
        """Fill registration form with human behavior"""
        try:
            logger.info("[FORM] Filling form with human behavior...")
            wait = WebDriverWait(self.driver, 10)
            
            # Quick glance at page
            logger.info("[HUMAN] Quick page check...")
            self.human_delay(0.5, 1.0)
            
            # Email - FAST
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.click()
            self.human_delay(0.2, 0.4)
            
            # Type fast without mistakes
            self.human_type(email_field, user_data['email'], make_mistakes=False)
            logger.info(f"[FORM] Email: {user_data['email']}")
            
            # Quick move to next
            self.human_delay(0.3, 0.6)
            
            # Quick scroll
            self.human_delay(0.2, 0.3)
            
            # Check for username, gender, country (long form)
            has_username = len(self.driver.find_elements(By.NAME, "username")) > 0
            has_gender = len(self.driver.find_elements(By.NAME, "gender")) > 0
            has_country = len(self.driver.find_elements(By.NAME, "country")) > 0
            
            # CRITICAL FIX: Fill optional fields FAST like a power user!
            if has_username or has_gender or has_country:
                logger.info(f"[FORM] Long form detected (username={has_username}, gender={has_gender}, country={has_country})")
                logger.info("[STRATEGY] Filling ALL fields QUICKLY like experienced user")
            
            # Fill username FAST
            if has_username:
                # Quick pause
                self.human_delay(0.3, 0.6)
                
                username_field = self.driver.find_element(By.NAME, "username")
                username_field.click()
                self.human_delay(0.2, 0.4)
                
                # Type fast without mistakes (power user)
                self.human_type(username_field, user_data['username'], make_mistakes=False)
                logger.info(f"[FORM] Username: {user_data['username']}")
                
                # Quick move to next
                self.human_delay(0.2, 0.4)
            
            # Fill gender FAST
            if has_gender:
                try:
                    # Quick pause
                    self.human_delay(0.2, 0.4)
                    
                    # Scroll to gender field
                    gender_element = self.driver.find_element(By.NAME, "gender")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", gender_element)
                    self.human_delay(0.3, 0.5)
                    
                    # Try Select class first (for standard select)
                    try:
                        gender_select = Select(gender_element)
                        gender_select.select_by_value(user_data['gender_value'])
                        logger.info(f"[FORM] Gender set via Select: {user_data['gender_value']}")
                    except Exception as select_error:
                        # If Select fails, it's a custom dropdown
                        logger.info(f"[FORM] Custom gender dropdown detected: {select_error}")
                        
                        # Click to open dropdown (click parent container if exists)
                        try:
                            parent = gender_element.find_element(By.XPATH, "./parent::*")
                            parent.click()
                        except:
                            gender_element.click()
                        
                        self.human_delay(0.8, 1.2)
                        
                        # Take screenshot to see dropdown options
                        self.take_screenshot("gender_dropdown_opened")
                        
                        # Find and click the option (multiple strategies)
                        option_found = False
                        
                        # Strategy 1: Try common dropdown selectors
                        option_selectors = [
                            f"//div[contains(@class, 'option') and (contains(text(), 'Male') or contains(text(), 'male'))]",
                            f"//li[contains(text(), 'Male') or contains(text(), 'male')]",
                            f"//*[@role='option' and (contains(text(), 'Male') or contains(text(), 'male'))]",
                            f"//div[contains(@class, 'dropdown')]//div[contains(text(), 'Male')]",
                            f"//div[contains(@class, 'select')]//div[contains(text(), 'Male')]"
                        ]
                        
                        if user_data['gender_value'] == 'female':
                            option_selectors = [
                                f"//div[contains(@class, 'option') and (contains(text(), 'Female') or contains(text(), 'female'))]",
                                f"//li[contains(text(), 'Female') or contains(text(), 'female')]",
                                f"//*[@role='option' and (contains(text(), 'Female') or contains(text(), 'female'))]",
                                f"//div[contains(@class, 'dropdown')]//div[contains(text(), 'Female')]",
                                f"//div[contains(@class, 'select')]//div[contains(text(), 'Female')]"
                            ]
                        
                        for selector in option_selectors:
                            try:
                                option = WebDriverWait(self.driver, 3).until(
                                    EC.presence_of_element_located((By.XPATH, selector))
                                )
                                # Scroll to option if needed
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", option)
                                self.human_delay(0.2, 0.4)
                                # Try click
                                try:
                                    option.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", option)
                                option_found = True
                                logger.info(f"[FORM] Gender option clicked: {user_data['gender_value']}")
                                break
                            except Exception as opt_error:
                                logger.debug(f"[FORM] Selector failed: {selector} - {opt_error}")
                                continue
                        
                        if not option_found:
                            logger.warning("[FORM] Could not find gender option, trying JS set")
                            # Fallback: set value directly via JS and trigger events
                            self.driver.execute_script(f"""
                                var el = arguments[0];
                                el.value = '{user_data['gender_value']}';
                                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                            """, gender_element)
                    
                    # Trigger validation events (multiple)
                    self.driver.execute_script("""
                        var el = arguments[0];
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('blur', { bubbles: true }));
                    """, gender_element)
                    
                    logger.info(f"[FORM] Gender: {user_data['gender_value']}")
                    self.human_delay(0.3, 0.6)
                except Exception as e:
                    logger.error(f"[FORM] Gender error: {e}")
                    self.take_screenshot("gender_error")
            
            # Birthday - always present
            # Longer pause before birthday (thinking)
            self.human_delay(1.5, 2.5)
            
            # Scroll to birthday section
            try:
                birthday_section = self.driver.find_element(By.NAME, "birthday_month")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", birthday_section)
                self.human_delay(0.5, 0.8)
            except:
                pass
            
            # Month
            month_element = wait.until(EC.presence_of_element_located((By.NAME, "birthday_month")))
            self.human_mouse_move(month_element)
            month_element.click()
            self.human_delay(0.5, 0.9)
            month_select = Select(month_element)
            month_select.select_by_visible_text(user_data['birth_month_text'])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", month_element)
            logger.info(f"[FORM] Month: {user_data['birth_month_text']}")
            self.human_delay(0.6, 1.0)
            
            # Day
            day_element = self.driver.find_element(By.NAME, "birthday_day")
            self.human_mouse_move(day_element)
            day_element.click()
            self.human_delay(0.5, 0.9)
            day_select = Select(day_element)
            day_select.select_by_value(user_data['birth_day'])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", day_element)
            logger.info(f"[FORM] Day: {user_data['birth_day']}")
            self.human_delay(0.6, 1.0)
            
            # Year
            year_element = self.driver.find_element(By.NAME, "birthday_year")
            self.human_mouse_move(year_element)
            year_element.click()
            self.human_delay(0.5, 0.9)
            year_select = Select(year_element)
            year_select.select_by_value(user_data['birth_year'])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", year_element)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", year_element)
            logger.info(f"[FORM] Year: {user_data['birth_year']}")
            self.human_delay(0.8, 1.5)
            
            # Click outside to trigger validation with random position
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                actions = ActionChains(self.driver)
                actions.move_to_element_with_offset(body, random.randint(100, 300), random.randint(50, 150))
                actions.click()
                actions.perform()
            except:
                pass
            self.human_delay(0.8, 1.5)
            
            # Fill country FAST
            if has_country:
                try:
                    # Quick pause
                    self.human_delay(0.2, 0.4)
                    
                    # Scroll to country field
                    country_element = self.driver.find_element(By.NAME, "country")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", country_element)
                    self.human_delay(0.3, 0.5)
                    
                    # Try Select class first (for standard select)
                    try:
                        country_select = Select(country_element)
                        try:
                            country_select.select_by_value("US")
                        except:
                            try:
                                country_select.select_by_visible_text("United States")
                            except:
                                country_select.select_by_index(1)
                        logger.info("[FORM] Country set via Select: United States")
                    except Exception as select_error:
                        # If Select fails, it's a custom dropdown
                        logger.info(f"[FORM] Custom country dropdown detected: {select_error}")
                        
                        # Click to open dropdown (click parent container if exists)
                        try:
                            parent = country_element.find_element(By.XPATH, "./parent::*")
                            parent.click()
                        except:
                            country_element.click()
                        
                        self.human_delay(0.8, 1.2)
                        
                        # Take screenshot to see dropdown options
                        self.take_screenshot("country_dropdown_opened")
                        
                        # Find and click United States option (multiple strategies)
                        option_found = False
                        option_selectors = [
                            "//div[contains(@class, 'option') and contains(text(), 'United States')]",
                            "//li[contains(text(), 'United States')]",
                            "//*[@role='option' and contains(text(), 'United States')]",
                            "//div[contains(@class, 'dropdown')]//div[contains(text(), 'United States')]",
                            "//div[contains(@class, 'select')]//div[contains(text(), 'United States')]",
                            "//div[contains(@class, 'option') and contains(text(), 'USA')]",
                            "//li[contains(text(), 'USA')]",
                            "//*[@role='option' and contains(text(), 'USA')]",
                            "//div[contains(@class, 'option') and contains(text(), 'US')]",
                            "//div[contains(@class, 'option') and @data-value='US']"
                        ]
                        
                        for selector in option_selectors:
                            try:
                                option = WebDriverWait(self.driver, 3).until(
                                    EC.presence_of_element_located((By.XPATH, selector))
                                )
                                # Scroll to option if needed
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", option)
                                self.human_delay(0.2, 0.4)
                                # Try click
                                try:
                                    option.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", option)
                                option_found = True
                                logger.info("[FORM] Country option clicked: United States")
                                break
                            except Exception as opt_error:
                                logger.debug(f"[FORM] Selector failed: {selector} - {opt_error}")
                                continue
                        
                        if not option_found:
                            logger.warning("[FORM] Could not find country option, trying JS set")
                            # Fallback: set value directly via JS and trigger events
                            self.driver.execute_script("""
                                var el = arguments[0];
                                el.value = 'US';
                                el.dispatchEvent(new Event('input', { bubbles: true }));
                                el.dispatchEvent(new Event('change', { bubbles: true }));
                                el.dispatchEvent(new Event('blur', { bubbles: true }));
                            """, country_element)
                    
                    # Trigger validation events (multiple)
                    self.driver.execute_script("""
                        var el = arguments[0];
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                        el.dispatchEvent(new Event('blur', { bubbles: true }));
                    """, country_element)
                    
                    logger.info("[FORM] Country: United States")
                    self.human_delay(0.3, 0.6)
                except Exception as e:
                    logger.error(f"[FORM] Country error: {e}")
                    self.take_screenshot("country_error")
            
            # Natural scroll back to top
            self.driver.execute_script("window.scrollTo({top: 0, behavior: 'smooth'});")
            self.human_delay(0.8, 1.3)
            
            # Simulate reviewing the form but faster
            logger.info("[HUMAN] Quick form review...")
            
            # Fewer but more natural mouse movements
            try:
                actions = ActionChains(self.driver)
                for _ in range(random.randint(2, 3)):
                    actions.move_by_offset(random.randint(-40, 40), random.randint(-25, 25))
                    actions.perform()
                    self.human_delay(0.4, 0.7)
                    actions.move_by_offset(0, 0)  # Reset
            except:
                pass
            
            # Shorter final pause (confident user)
            self.human_delay(1.0, 2.0)
            
            logger.info("[FORM] Form filled successfully with human behavior")
            return True
            
        except Exception as e:
            logger.error(f"[FORM] Error: {e}")
            return False
    
    def submit_form(self):
        """Submit form with human behavior"""
        try:
            logger.info("[SUBMIT] Looking for submit button...")
            wait = WebDriverWait(self.driver, 10)
            
            # Check for validation errors first
            try:
                error_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'invalid')]")
                if error_elements:
                    for err in error_elements:
                        if err.is_displayed():
                            logger.error(f"[VALIDATION] Error found: {err.text}")
            except:
                pass
            
            # Moderate pause before checkbox
            self.human_delay(0.8, 1.5)
            
            # Try to find and check terms checkbox
            try:
                checkbox = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='checkbox']")
                ))
                if not checkbox.is_selected():
                    # Scroll to checkbox
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", checkbox)
                    self.human_delay(0.5, 0.9)
                    
                    self.human_mouse_move(checkbox)
                    self.human_delay(0.6, 1.0)
                    checkbox.click()
                    logger.info("[SUBMIT] Terms checkbox checked")
                    
                    # Quick pause after checking
                    self.human_delay(0.7, 1.2)
            except:
                logger.info("[SUBMIT] No terms checkbox found")
            
            # Find Next button
            button_xpaths = [
                "//button[contains(normalize-space(), 'Next')]",
                "//button[contains(text(), 'Next')]",
                "//button[@type='submit']"
            ]
            
            button = None
            for xpath in button_xpaths:
                try:
                    button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    logger.info(f"[SUBMIT] Found button with XPath: {xpath}")
                    break
                except:
                    continue
            
            if not button:
                logger.error("[SUBMIT] Could not find submit button")
                return False
            
            # Scroll to button
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", button)
            self.human_delay(0.5, 0.9)
            
            # Human behavior before clicking (confident)
            self.human_mouse_move(button)
            self.human_delay(1.0, 2.0)  # Moderate thinking time
            
            # Try pressing ENTER instead of clicking (more human-like)
            logger.info("[SUBMIT] Pressing ENTER to submit...")
            from selenium.webdriver.common.keys import Keys
            try:
                # Press ENTER on the button
                button.send_keys(Keys.ENTER)
                logger.info("[SUBMIT] Form submitted (ENTER key)")
            except:
                try:
                    # Fallback to regular click
                    button.click()
                    logger.info("[SUBMIT] Form submitted (click)")
                except:
                    # Last resort: JS click
                    self.driver.execute_script("arguments[0].click();", button)
                    logger.info("[SUBMIT] Form submitted (JS click)")
            
            self.human_delay(2, 3)
            return True
            
        except Exception as e:
            logger.error(f"[SUBMIT] Error: {e}")
            return False
    
    def wait_for_result(self, timeout=30):
        """Wait for registration result"""
        try:
            logger.info(f"[WAIT] Waiting up to {timeout}s for result...")
            
            # Wait with shorter intervals and check connection
            for i in range(timeout):
                try:
                    # Check current state
                    current_url = self.driver.current_url
                    page_text = self.driver.page_source.lower()
                    
                    # Success indicators
                    if "password" in page_text or "verify" in page_text or "create a password" in page_text:
                        logger.info("[SUCCESS] Registration successful - moved to next step!")
                        return True
                    
                    # Error indicators  
                    if "not available" in page_text:
                        logger.error("[FAIL] Registration not available (Bot detected)")
                        return False
                    
                    # Check if URL changed (success)
                    if "/register/password" in current_url or "/register/verify" in current_url:
                        logger.info(f"[SUCCESS] URL changed to: {current_url}")
                        return True
                    
                    # Check if form got LONGER (Rumble redirect trick)
                    # If username field appears = they want more info
                    if i > 3:  # After 3 seconds, check for form changes
                        has_username = len(self.driver.find_elements(By.NAME, "username")) > 0
                        if has_username:
                            logger.warning("[DETECT] Form changed to LONG form - need to fill additional fields!")
                            return "LONG_FORM"  # Special return value
                    
                    # CAPTCHA - but don't loop forever
                    if i > 15:  # After 15 seconds, assume it's stuck
                        logger.warning("[TIMEOUT] Waiting too long, checking page state...")
                        # If no error message, might be success
                        if "not available" not in page_text and "error" not in page_text.lower():
                            logger.info("[INFO] No error found, assuming success")
                            return True
                    
                    # Check if moved to next page
                    if current_url != self.driver.current_url:
                        logger.info(f"[INFO] URL changed to: {current_url}")
                    
                except Exception as e:
                    logger.warning(f"[WARN] Error checking page state: {e}")
                    # Connection lost, browser might have crashed
                    return False
                
                time.sleep(1)
            
            # Timeout reached
            logger.error(f"[TIMEOUT] No response after {timeout}s")
            try:
                logger.info(f"[INFO] Final URL: {self.driver.current_url}")
            except:
                logger.error("[ERROR] Cannot get URL - browser crashed")
            return False
            
        except Exception as e:
            logger.error(f"[ERROR] wait_for_result crashed: {e}")
            return False
    
    def take_screenshot(self, name):
        """Take screenshot"""
        try:
            log_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(log_dir, exist_ok=True)
            filename = os.path.join(log_dir, f"screenshot_{name}_{int(time.time())}.png")
            
            # Try to take screenshot, skip if browser crashed
            try:
                self.driver.save_screenshot(filename)
                logger.info(f"[SCREENSHOT] {filename}")
                return filename
            except Exception as screenshot_error:
                logger.warning(f"[SCREENSHOT] Failed (browser may have crashed): {screenshot_error}")
                return None
        except Exception as e:
            logger.error(f"[SCREENSHOT] Error: {e}")
            return None
    
    def run(self, num_attempts=1):
        """Run registration with multiple attempts"""
        success_count = 0
        
        for attempt in range(1, num_attempts + 1):
            logger.info("="*60)
            logger.info(f"[ATTEMPT {attempt}/{num_attempts}] Starting @ {datetime.now().strftime('%H:%M:%S')}")
            logger.info("="*60)
            
            try:
                # Navigate
                if not self.navigate_to_registration():
                    logger.error(f"[ATTEMPT {attempt}] Navigation failed")
                    continue
                
                self.take_screenshot(f"attempt{attempt}_01_loaded")
                
                # Check CAPTCHA initially
                self.detect_and_solve_captcha(timeout=60)
                self.human_delay(1, 2)
                
                # Generate and fill form
                user_data = self.generate_user_data()
                logger.info(f"[USER] {user_data['email']}")
                
                if not self.fill_form(user_data):
                    logger.error(f"[ATTEMPT {attempt}] Form fill failed")
                    self.take_screenshot(f"attempt{attempt}_02_fill_error")
                    continue
                
                self.take_screenshot(f"attempt{attempt}_03_filled")
                
                # Check CAPTCHA after filling
                self.detect_and_solve_captcha(timeout=60)
                self.human_delay(1, 2)
                
                # Submit
                if not self.submit_form():
                    logger.error(f"[ATTEMPT {attempt}] Submit failed")
                    self.take_screenshot(f"attempt{attempt}_04_submit_error")
                    continue
                
                self.take_screenshot(f"attempt{attempt}_05_submitted")
                
                # Check CAPTCHA after submit
                try:
                    self.detect_and_solve_captcha(timeout=120)
                except Exception as captcha_error:
                    logger.warning(f"[CAPTCHA] Post-submit check failed: {captcha_error}")
                
                # Wait for result
                result = self.wait_for_result(timeout=40)
                
                self.take_screenshot(f"attempt{attempt}_06_result")
                
                # Handle LONG_FORM redirect
                if result == "LONG_FORM":
                    logger.info("[REDIRECT] Rumble wants long form, filling additional fields...")
                    self.human_delay(1, 2)
                    
                    # Fill the long form
                    if not self.fill_form(user_data):
                        logger.error(f"[ATTEMPT {attempt}] Long form fill failed")
                        self.take_screenshot(f"attempt{attempt}_07_long_form_error")
                        continue
                    
                    self.take_screenshot(f"attempt{attempt}_07_long_form_filled")
                    
                    # Check CAPTCHA
                    self.detect_and_solve_captcha(timeout=60)
                    self.human_delay(1, 2)
                    
                    # Submit again
                    if not self.submit_form():
                        logger.error(f"[ATTEMPT {attempt}] Long form submit failed")
                        self.take_screenshot(f"attempt{attempt}_08_long_submit_error")
                        continue
                    
                    self.take_screenshot(f"attempt{attempt}_08_long_form_submitted")
                    
                    # Check CAPTCHA after submit
                    try:
                        self.detect_and_solve_captcha(timeout=120)
                    except Exception as captcha_error:
                        logger.warning(f"[CAPTCHA] Long form post-submit check failed: {captcha_error}")
                    
                    # Wait for final result
                    result = self.wait_for_result(timeout=40)
                    self.take_screenshot(f"attempt{attempt}_09_final_result")
                
                if result == True:
                    success_count += 1
                    logger.info(f"[SUCCESS] Attempt {attempt} succeeded!")
                else:
                    logger.error(f"[FAIL] Attempt {attempt} failed")
                
                # Delay before next attempt
                if attempt < num_attempts:
                    delay = random.randint(5, 10)
                    logger.info(f"[DELAY] Waiting {delay}s before next attempt...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.exception(f"[ERROR] Attempt {attempt} crashed: {e}")
                self.take_screenshot(f"attempt{attempt}_error")
        
        # Summary
        logger.info("="*60)
        logger.info(f"[SUMMARY] {success_count}/{num_attempts} attempts succeeded")
        logger.info("="*60)
        
        return success_count > 0
    
    def close(self):
        """Close browser"""
        try:
            if self.driver:
                logger.info("[CLOSE] Closing browser...")
                self.driver.quit()
                logger.info("[CLOSE] Browser closed")
        except Exception as e:
            logger.error(f"[CLOSE] Error: {e}")

def main():
    print("="*60)
    print("RUMBLE ULTIMATE BYPASS - FINAL VERSION")
    print("All stealth techniques + CAPTCHA solver")
    print("="*60)
    
    # Configuration
    use_proxy = None  # Set to "http://user:pass@host:port" if using proxy
    num_attempts = 1  # Number of registration attempts
    
    # Email file path (put your file here)
    email_file = "outlook.txt"  # Or full path: r"C:\path\to\file.txt"
    
    register = None
    try:
        register = RumbleUltimateBypass(use_proxy=use_proxy, email_file=email_file)
        
        if not register.driver:
            print("[ERROR] Failed to initialize driver")
            return
        
        success = register.run(num_attempts=num_attempts)
        
        if success:
            print("\n" + "="*60)
            print("[SUCCESS] At least one registration succeeded!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("[FAILED] All attempts failed")
            print("="*60)
        
        # Keep browser open
        logger.info("\nKeeping browser open for 10 seconds...")
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\n[STOP] User interrupted")
    except Exception as e:
        logger.exception(f"[FATAL] Error: {e}")
    finally:
        if register:
            register.close()

if __name__ == "__main__":
    main()
