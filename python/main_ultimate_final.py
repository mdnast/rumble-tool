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
    def __init__(self, use_proxy=None):
        """
        Initialize Ultimate Bypass
        Args:
            use_proxy: Proxy string (e.g., "http://user:pass@host:port")
        """
        self.driver = None
        self.captcha_solver = None
        self.use_proxy = use_proxy
        
        # Initialize CAPTCHA solver
        if HAS_CAPTCHA_SOLVER:
            try:
                self.captcha_solver = CaptchaSolver(
                    local_api_key=Config.LOCAL_CAPTCHA_API_KEY,
                    nextcaptcha_client_key=Config.NEXTCAPTCHA_CLIENT_KEY
                )
                logger.info("[CAPTCHA] Solver initialized")
            except Exception as e:
                logger.warning(f"[CAPTCHA] Could not initialize: {e}")
        
        self.setup_driver()
    
    def setup_driver(self):
        """Setup undetected Chrome with all stealth options"""
        try:
            logger.info("[DRIVER] Initializing ULTIMATE undetected Chrome...")
            
            options = uc.ChromeOptions()
            
            # Basic anti-detection
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            
            # Random window size
            width = random.randint(1200, 1920)
            height = random.randint(800, 1080)
            options.add_argument(f'--window-size={width},{height}')
            
            # Random user agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Proxy
            if self.use_proxy:
                options.add_argument(f'--proxy-server={self.use_proxy}')
                logger.info(f"[PROXY] Using proxy: {self.use_proxy}")
            
            # Additional prefs (excludeSwitches not supported in undetected-chromedriver)
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
            }
            options.add_experimental_option("prefs", prefs)
            
            # Initialize driver
            self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
            
            # Inject stealth scripts
            self.inject_stealth_scripts()
            
            # Set implicit wait
            self.driver.implicitly_wait(10)
            
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
    
    def human_type(self, element, text):
        """Type text like a human with random delays"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        self.human_delay(0.3, 0.6)
    
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
    
    def generate_user_data(self):
        """Generate random user data"""
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
        
        # Random birthday (18-30 years old)
        years_ago = random.randint(18, 30)
        birth_date = datetime.now() - timedelta(days=years_ago * 365 + random.randint(0, 365))
        
        months = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        
        return {
            'email': f"{random_str}.{random.randint(1000, 9999)}@outlook.com",
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
            
            # Human behavior: scroll a bit
            self.driver.execute_script("window.scrollTo(0, 100);")
            self.human_delay(1, 2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.human_delay(1, 2)
            
            return True
            
        except Exception as e:
            logger.error(f"[NAV] Failed: {e}")
            return False
    
    def detect_and_solve_captcha(self, timeout=120):
        """Detect and solve Cloudflare Turnstile"""
        if not self.captcha_solver:
            logger.info("[CAPTCHA] No solver configured")
            return True
        
        try:
            # Check for Turnstile
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                if "challenges.cloudflare.com" in src or "turnstile" in src.lower():
                    logger.info("[CAPTCHA] Cloudflare Turnstile detected!")
                    
                    # Extract sitekey
                    import re
                    page_source = self.driver.page_source
                    
                    sitekey = None
                    match = re.search(r'data-sitekey="([^"]+)"', page_source)
                    if match:
                        sitekey = match.group(1)
                    
                    if not sitekey:
                        match = re.search(r'sitekey=([^&]+)', src)
                        if match:
                            sitekey = match.group(1)
                    
                    if sitekey:
                        logger.info(f"[CAPTCHA] Sitekey: {sitekey}")
                        logger.info("[CAPTCHA] Solving with API...")
                        
                        token = self.captcha_solver.solve_turnstile(
                            self.driver.current_url, 
                            sitekey, 
                            timeout
                        )
                        
                        if token:
                            logger.info("[CAPTCHA] Token received, injecting...")
                            
                            # Inject token
                            script = f"""
                            var forms = document.querySelectorAll('form');
                            for (var i = 0; i < forms.length; i++) {{
                                var input = document.createElement('input');
                                input.type = 'hidden';
                                input.name = 'cf-turnstile-response';
                                input.value = '{token}';
                                forms[i].appendChild(input);
                            }}
                            
                            var textarea = document.querySelector('textarea[name="cf-turnstile-response"]');
                            if (textarea) textarea.value = '{token}';
                            """
                            
                            self.driver.execute_script(script)
                            logger.info("[CAPTCHA] Token injected successfully")
                            self.human_delay(2, 3)
                            return True
                        else:
                            logger.error("[CAPTCHA] Failed to solve")
                            return False
                    else:
                        logger.error("[CAPTCHA] Could not find sitekey")
                        return False
            
            logger.info("[CAPTCHA] No CAPTCHA detected")
            return True
            
        except Exception as e:
            logger.error(f"[CAPTCHA] Error: {e}")
            return False
    
    def fill_form(self, user_data):
        """Fill registration form with human behavior"""
        try:
            logger.info("[FORM] Filling form with human behavior...")
            wait = WebDriverWait(self.driver, 10)
            
            # Email - with human behavior
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            self.human_mouse_move(email_field)
            email_field.click()
            self.human_delay(0.5, 1)
            self.human_type(email_field, user_data['email'])
            logger.info(f"[FORM] Email: {user_data['email']}")
            
            # Random scroll
            self.driver.execute_script("window.scrollTo(0, 50);")
            self.human_delay(0.5, 1)
            
            # Check for username, gender, country (long form)
            has_username = len(self.driver.find_elements(By.NAME, "username")) > 0
            has_gender = len(self.driver.find_elements(By.NAME, "gender")) > 0
            has_country = len(self.driver.find_elements(By.NAME, "country")) > 0
            
            if has_username:
                username_field = self.driver.find_element(By.NAME, "username")
                self.human_mouse_move(username_field)
                username_field.click()
                self.human_delay(0.5, 1)
                self.human_type(username_field, user_data['username'])
                logger.info(f"[FORM] Username: {user_data['username']}")
            
            if has_gender:
                try:
                    # Wait for gender dropdown
                    gender_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.NAME, "gender"))
                    )
                    
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gender_element)
                    self.human_delay(0.5, 0.8)
                    
                    # Try using keyboard navigation (more natural)
                    from selenium.webdriver.common.keys import Keys
                    
                    # Click to focus
                    gender_element.click()
                    self.human_delay(0.3, 0.6)
                    
                    # Use arrow keys to select
                    if user_data['gender_value'] == 'male':
                        # Usually male is first option
                        gender_element.send_keys(Keys.ARROW_DOWN)
                        self.human_delay(0.2, 0.4)
                    elif user_data['gender_value'] == 'female':
                        # Female is usually second
                        gender_element.send_keys(Keys.ARROW_DOWN)
                        self.human_delay(0.2, 0.4)
                        gender_element.send_keys(Keys.ARROW_DOWN)
                        self.human_delay(0.2, 0.4)
                    
                    # Press Enter to confirm
                    gender_element.send_keys(Keys.ENTER)
                    self.human_delay(0.5, 0.8)
                    
                    logger.info(f"[FORM] Gender: {user_data['gender_value']} (keyboard)")
                    
                    # Click outside
                    self.driver.find_element(By.TAG_NAME, "body").click()
                    self.human_delay(0.5, 1.0)
                except Exception as e:
                    logger.error(f"[FORM] Gender error: {e}")
                    self.take_screenshot("gender_error")
            
            # Birthday - always present
            self.human_delay(0.5, 1)
            
            # Month
            month_element = wait.until(EC.presence_of_element_located((By.NAME, "birthday_month")))
            month_element.click()
            self.human_delay(0.3, 0.6)
            month_select = Select(month_element)
            month_select.select_by_visible_text(user_data['birth_month_text'])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", month_element)
            logger.info(f"[FORM] Month: {user_data['birth_month_text']}")
            self.human_delay(0.3, 0.7)
            
            # Day
            day_element = self.driver.find_element(By.NAME, "birthday_day")
            day_element.click()
            self.human_delay(0.3, 0.6)
            day_select = Select(day_element)
            day_select.select_by_value(user_data['birth_day'])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", day_element)
            logger.info(f"[FORM] Day: {user_data['birth_day']}")
            self.human_delay(0.3, 0.7)
            
            # Year
            year_element = self.driver.find_element(By.NAME, "birthday_year")
            year_element.click()
            self.human_delay(0.3, 0.6)
            year_select = Select(year_element)
            year_select.select_by_value(user_data['birth_year'])
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", year_element)
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", year_element)
            logger.info(f"[FORM] Year: {user_data['birth_year']}")
            self.human_delay(0.5, 1)
            
            # Click outside to trigger validation
            try:
                self.driver.find_element(By.TAG_NAME, "body").click()
            except:
                pass
            self.human_delay(0.5, 1)
            
            if has_country:
                try:
                    # Wait for country dropdown
                    country_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.NAME, "country"))
                    )
                    
                    # Scroll into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", country_element)
                    self.human_delay(0.5, 0.8)
                    
                    # Use keyboard to type and select
                    from selenium.webdriver.common.keys import Keys
                    
                    # Click to focus
                    country_element.click()
                    self.human_delay(0.3, 0.6)
                    
                    # Type "United" to search
                    country_element.send_keys("United")
                    self.human_delay(0.5, 0.8)
                    
                    # Press Enter to select first match (United States)
                    country_element.send_keys(Keys.ENTER)
                    self.human_delay(0.5, 0.8)
                    
                    logger.info("[FORM] Country: United States (keyboard)")
                    
                    # Click outside
                    self.driver.find_element(By.TAG_NAME, "body").click()
                    self.human_delay(0.5, 1.0)
                except Exception as e:
                    logger.error(f"[FORM] Country error: {e}")
                    self.take_screenshot("country_error")
            
            # Random scroll again
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.human_delay(0.5, 1)
            
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
            
            # Try to find and check terms checkbox
            try:
                checkbox = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='checkbox']")
                ))
                if not checkbox.is_selected():
                    self.human_mouse_move(checkbox)
                    self.human_delay(0.5, 1)
                    checkbox.click()
                    logger.info("[SUBMIT] Terms checkbox checked")
                    self.human_delay(0.5, 1)
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
            
            # Human behavior before clicking
            self.human_mouse_move(button)
            self.human_delay(1, 2)
            
            logger.info("[SUBMIT] Clicking submit button...")
            try:
                self.driver.execute_script("arguments[0].click();", button)
                logger.info("[SUBMIT] Form submitted (JS click)")
            except:
                button.click()
                logger.info("[SUBMIT] Form submitted (regular click)")
            
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
                    if "password" in page_text or "verify" in page_text:
                        logger.info("[SUCCESS] Registration successful!")
                        return True
                    
                    # Error indicators
                    if "not available" in page_text:
                        logger.error("[FAIL] Registration not available (Bot detected)")
                        return False
                    
                    # CAPTCHA appeared
                    if "captcha" in current_url or "challenge" in current_url or "turnstile" in page_text:
                        logger.warning("[CAPTCHA] CAPTCHA detected after submit")
                        if self.detect_and_solve_captcha(timeout=120):
                            logger.info("[CAPTCHA] Solved, waiting for next page...")
                            time.sleep(3)
                            continue
                        return False
                    
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
                
                if result:
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
    
    register = None
    try:
        register = RumbleUltimateBypass(use_proxy=use_proxy)
        
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
