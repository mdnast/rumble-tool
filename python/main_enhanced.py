"""
RUMBLE ENHANCED BYPASS - With Advanced Stealth
- Bezier curve mouse movement
- Typo simulation
- Advanced fingerprinting
- Session warmup
- Local CAPTCHA solver API
"""

import time
import logging
import os
import random
import string
from datetime import datetime, timedelta

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Import modules
try:
    from captcha_solver import CaptchaSolver
    from config import Config
    from advanced_stealth import (
        HumanBehaviorAdvanced, 
        AdvancedFingerprint, 
        SessionWarmup
    )
    HAS_ADVANCED = True
except Exception as e:
    print(f"[WARN] Could not import advanced modules: {e}")
    HAS_ADVANCED = False

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rumble_enhanced.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RumbleEnhancedBypass:
    def __init__(self, use_proxy=None, enable_warmup=True):
        """
        Initialize Enhanced Bypass
        Args:
            use_proxy: Proxy string (e.g., "http://user:pass@host:port")
            enable_warmup: Enable session warmup (default: True)
        """
        self.driver = None
        self.captcha_solver = None
        self.use_proxy = use_proxy
        self.enable_warmup = enable_warmup
        
        # Initialize CAPTCHA solver with local API
        try:
            self.captcha_solver = CaptchaSolver(
                local_api_key=Config.LOCAL_CAPTCHA_API_KEY,
                nextcaptcha_client_key=Config.NEXTCAPTCHA_CLIENT_KEY
            )
            logger.info("[CAPTCHA] Solver initialized with local API")
        except Exception as e:
            logger.warning(f"[CAPTCHA] Could not initialize: {e}")
        
        self.setup_driver()
    
    def setup_driver(self):
        """Setup undetected Chrome with enhanced stealth"""
        try:
            logger.info("[DRIVER] Initializing ENHANCED undetected Chrome...")
            
            options = uc.ChromeOptions()
            
            # Anti-detection flags
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            
            # Random window size
            width = random.randint(1280, 1920)
            height = random.randint(800, 1080)
            options.add_argument(f'--window-size={width},{height}')
            
            # Random user agent
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # Language
            options.add_argument('--lang=en-US')
            
            # Proxy
            if self.use_proxy:
                options.add_argument(f'--proxy-server={self.use_proxy}')
                logger.info(f"[PROXY] Using: {self.use_proxy}")
            
            # Prefs
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2,
                "intl.accept_languages": "en-US,en"
            }
            options.add_experimental_option("prefs", prefs)
            
            # Initialize driver
            self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
            
            # Inject advanced fingerprint protection
            if HAS_ADVANCED:
                AdvancedFingerprint.inject_fingerprint(self.driver)
            
            self.driver.implicitly_wait(10)
            
            logger.info("[DRIVER] ENHANCED Chrome initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"[DRIVER] Failed to initialize: {e}")
            return False
    
    def human_delay(self, min_sec=0.5, max_sec=2.0):
        """Random human-like delay"""
        time.sleep(random.uniform(min_sec, max_sec))
    
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
        """Navigate to registration with warmup"""
        try:
            # Warmup session first
            if self.enable_warmup and HAS_ADVANCED:
                logger.info("[WARMUP] Performing session warmup...")
                try:
                    SessionWarmup.warmup(self.driver, "https://rumble.com")
                    self.human_delay(2, 3)
                except Exception as warmup_error:
                    logger.warning(f"[WARMUP] Error: {warmup_error}, continuing anyway")
            
            # Navigate to registration
            url = "https://rumble.com/register/"
            logger.info(f"[NAV] Navigating to: {url}")
            
            try:
                self.driver.get(url)
            except Exception as nav_error:
                logger.warning(f"[NAV] Get URL error: {nav_error}, retrying...")
                time.sleep(2)
                self.driver.get(url)
            
            # Wait for page load with longer timeout
            logger.info("[NAV] Waiting for page to load...")
            
            # First wait for document ready
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logger.info("[NAV] Document ready")
            
            # Wait for loading spinner to disappear
            logger.info("[NAV] Waiting for loading spinner...")
            time.sleep(3)  # Give time for any spinners to appear first
            
            try:
                # Wait for spinner to disappear (if present)
                WebDriverWait(self.driver, 20).until_not(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "svg[class*='spinner'], div[class*='loading'], div[class*='spinner']"))
                )
                logger.info("[NAV] Loading spinner gone")
            except:
                logger.info("[NAV] No loading spinner detected")
            
            # Now wait for form elements
            logger.info("[NAV] Waiting for form elements...")
            try:
                # Try multiple selectors
                WebDriverWait(self.driver, 30).until(
                    lambda d: d.find_element(By.NAME, "email") or 
                             d.find_element(By.CSS_SELECTOR, "input[type='email']") or
                             d.find_element(By.XPATH, "//input[@placeholder='Email' or @name='email']")
                )
                logger.info("[NAV] Form elements found")
            except TimeoutException:
                logger.warning("[NAV] Email field still not found after waiting")
            
            # Extra wait for dynamic content
            time.sleep(3)
            
            logger.info("[NAV] Registration page loaded")
            
            # Human behavior
            try:
                if HAS_ADVANCED:
                    HumanBehaviorAdvanced.scroll_naturally(self.driver)
                    HumanBehaviorAdvanced.random_reading_pause(1, 2)
                else:
                    self.driver.execute_script("window.scrollTo(0, 100);")
                    self.human_delay(1, 2)
            except Exception as behavior_error:
                logger.warning(f"[NAV] Behavior simulation error: {behavior_error}")
            
            return True
            
        except Exception as e:
            logger.error(f"[NAV] Failed: {e}")
            # Take screenshot for debugging
            try:
                self.take_screenshot("nav_error")
            except:
                pass
            return False
    
    def detect_and_solve_captcha(self, timeout=120):
        """Detect and solve Cloudflare Turnstile"""
        if not self.captcha_solver:
            logger.info("[CAPTCHA] No solver configured")
            return True
        
        try:
            # Check for Turnstile iframe
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                if "challenges.cloudflare.com" in src or "turnstile" in src.lower():
                    logger.info("[CAPTCHA] Cloudflare Turnstile detected!")
                    
                    # Extract sitekey
                    import re
                    page_source = self.driver.page_source
                    
                    sitekey = None
                    # Method 1: data-sitekey attribute
                    match = re.search(r'data-sitekey="([^"]+)"', page_source)
                    if match:
                        sitekey = match.group(1)
                    
                    # Method 2: from iframe src
                    if not sitekey:
                        match = re.search(r'sitekey=([^&\s]+)', src)
                        if match:
                            sitekey = match.group(1)
                    
                    # Method 3: search in script tags
                    if not sitekey:
                        match = re.search(r'"sitekey"\s*:\s*"([^"]+)"', page_source)
                        if match:
                            sitekey = match.group(1)
                    
                    if sitekey:
                        logger.info(f"[CAPTCHA] Sitekey found: {sitekey}")
                        logger.info("[CAPTCHA] Solving with API...")
                        
                        # Solve CAPTCHA
                        token = self.captcha_solver.solve_turnstile(
                            self.driver.current_url, 
                            sitekey, 
                            timeout
                        )
                        
                        if token:
                            logger.info("[CAPTCHA] Token received!")
                            logger.info(f"[CAPTCHA] Token preview: {token[:50]}...")
                            
                            # Inject token into page
                            script = f"""
                            // Method 1: Inject into forms
                            var forms = document.querySelectorAll('form');
                            for (var i = 0; i < forms.length; i++) {{
                                var input = document.createElement('input');
                                input.type = 'hidden';
                                input.name = 'cf-turnstile-response';
                                input.value = '{token}';
                                forms[i].appendChild(input);
                            }}
                            
                            // Method 2: Update existing textarea
                            var textarea = document.querySelector('textarea[name="cf-turnstile-response"]');
                            if (textarea) {{
                                textarea.value = '{token}';
                            }}
                            
                            // Method 3: Set on window
                            window.turnstileToken = '{token}';
                            
                            console.log('Turnstile token injected');
                            """
                            
                            self.driver.execute_script(script)
                            logger.info("[CAPTCHA] Token injected successfully")
                            self.human_delay(2, 3)
                            return True
                        else:
                            logger.error("[CAPTCHA] Failed to solve")
                            return False
                    else:
                        logger.error("[CAPTCHA] Could not extract sitekey")
                        return False
            
            logger.info("[CAPTCHA] No CAPTCHA detected")
            return True
            
        except Exception as e:
            logger.error(f"[CAPTCHA] Error: {e}")
            return False
    
    def fill_form(self, user_data):
        """Fill form with advanced human behavior"""
        try:
            logger.info("[FORM] Filling form with ENHANCED behavior...")
            wait = WebDriverWait(self.driver, 10)
            
            # Email
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            if HAS_ADVANCED:
                HumanBehaviorAdvanced.human_mouse_move(self.driver, email_field)
            email_field.click()
            self.human_delay(0.5, 1)
            
            if HAS_ADVANCED:
                HumanBehaviorAdvanced.human_type_with_mistakes(email_field, user_data['email'], 0.1)
            else:
                for char in user_data['email']:
                    email_field.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
            
            logger.info(f"[FORM] Email: {user_data['email']}")
            
            # Small reading pause
            if HAS_ADVANCED:
                HumanBehaviorAdvanced.random_reading_pause(1, 2)
            else:
                self.human_delay(1, 2)
            
            # Check for long form fields
            has_username = len(self.driver.find_elements(By.NAME, "username")) > 0
            has_gender = len(self.driver.find_elements(By.NAME, "gender")) > 0
            has_country = len(self.driver.find_elements(By.NAME, "country")) > 0
            
            if has_username:
                username_field = self.driver.find_element(By.NAME, "username")
                if HAS_ADVANCED:
                    HumanBehaviorAdvanced.human_mouse_move(self.driver, username_field)
                username_field.click()
                self.human_delay(0.5, 1)
                
                if HAS_ADVANCED:
                    HumanBehaviorAdvanced.human_type_with_mistakes(username_field, user_data['username'], 0.1)
                else:
                    for char in user_data['username']:
                        username_field.send_keys(char)
                        time.sleep(random.uniform(0.05, 0.15))
                
                logger.info(f"[FORM] Username: {user_data['username']}")
                self.human_delay(1, 2)
            
            if has_gender:
                try:
                    gender_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.NAME, "gender"))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gender_element)
                    self.human_delay(0.5, 0.8)
                    
                    gender_element.click()
                    self.human_delay(0.3, 0.6)
                    
                    if user_data['gender_value'] == 'male':
                        gender_element.send_keys(Keys.ARROW_DOWN)
                        self.human_delay(0.2, 0.4)
                    elif user_data['gender_value'] == 'female':
                        gender_element.send_keys(Keys.ARROW_DOWN)
                        self.human_delay(0.2, 0.4)
                        gender_element.send_keys(Keys.ARROW_DOWN)
                        self.human_delay(0.2, 0.4)
                    
                    gender_element.send_keys(Keys.ENTER)
                    self.human_delay(0.5, 0.8)
                    
                    logger.info(f"[FORM] Gender: {user_data['gender_value']}")
                    
                    self.driver.find_element(By.TAG_NAME, "body").click()
                    self.human_delay(0.5, 1.0)
                except Exception as e:
                    logger.error(f"[FORM] Gender error: {e}")
            
            # Birthday
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
            logger.info(f"[FORM] Year: {user_data['birth_year']}")
            self.human_delay(0.5, 1)
            
            # Country
            if has_country:
                try:
                    country_element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.NAME, "country"))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", country_element)
                    self.human_delay(0.5, 0.8)
                    
                    country_element.click()
                    self.human_delay(0.3, 0.6)
                    
                    country_element.send_keys("United")
                    self.human_delay(0.5, 0.8)
                    country_element.send_keys(Keys.ENTER)
                    self.human_delay(0.5, 0.8)
                    
                    logger.info("[FORM] Country: United States")
                    
                    self.driver.find_element(By.TAG_NAME, "body").click()
                    self.human_delay(0.5, 1.0)
                except Exception as e:
                    logger.error(f"[FORM] Country error: {e}")
            
            logger.info("[FORM] Form filled successfully")
            return True
            
        except Exception as e:
            logger.error(f"[FORM] Error: {e}")
            return False
    
    def submit_form(self):
        """Submit form with human behavior"""
        try:
            logger.info("[SUBMIT] Preparing to submit...")
            wait = WebDriverWait(self.driver, 10)
            
            # Check terms checkbox
            try:
                checkbox = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='checkbox']")
                ))
                if not checkbox.is_selected():
                    if HAS_ADVANCED:
                        HumanBehaviorAdvanced.human_mouse_move(self.driver, checkbox)
                    self.human_delay(0.5, 1)
                    checkbox.click()
                    logger.info("[SUBMIT] Terms checkbox checked")
                    self.human_delay(0.5, 1)
            except:
                logger.info("[SUBMIT] No terms checkbox")
            
            # Find submit button
            button_xpaths = [
                "//button[contains(normalize-space(), 'Next')]",
                "//button[contains(text(), 'Next')]",
                "//button[@type='submit']"
            ]
            
            button = None
            for xpath in button_xpaths:
                try:
                    button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    logger.info(f"[SUBMIT] Found button: {xpath}")
                    break
                except:
                    continue
            
            if not button:
                logger.error("[SUBMIT] Submit button not found")
                return False
            
            # Human behavior before submit
            if HAS_ADVANCED:
                HumanBehaviorAdvanced.human_mouse_move(self.driver, button)
                HumanBehaviorAdvanced.random_reading_pause(1, 2)
            else:
                self.human_delay(1, 2)
            
            logger.info("[SUBMIT] Clicking submit...")
            try:
                self.driver.execute_script("arguments[0].click();", button)
                logger.info("[SUBMIT] Submitted (JS click)")
            except:
                button.click()
                logger.info("[SUBMIT] Submitted (regular click)")
            
            self.human_delay(2, 3)
            return True
            
        except Exception as e:
            logger.error(f"[SUBMIT] Error: {e}")
            return False
    
    def wait_for_result(self, timeout=40):
        """Wait for registration result"""
        try:
            logger.info(f"[WAIT] Waiting up to {timeout}s for result...")
            
            for i in range(timeout):
                try:
                    current_url = self.driver.current_url
                    page_text = self.driver.page_source.lower()
                    
                    # Success
                    if "password" in page_text or "verify" in page_text:
                        logger.info("[SUCCESS] Registration successful!")
                        return True
                    
                    # Error
                    if "not available" in page_text:
                        logger.error("[FAIL] Registration not available")
                        return False
                    
                    # CAPTCHA appeared
                    if "captcha" in current_url or "challenge" in current_url or "turnstile" in page_text:
                        logger.warning("[CAPTCHA] CAPTCHA appeared after submit")
                        if self.detect_and_solve_captcha(timeout=120):
                            logger.info("[CAPTCHA] Solved, continuing...")
                            time.sleep(3)
                            continue
                        return False
                    
                except Exception as e:
                    logger.warning(f"[WARN] Check error: {e}")
                    return False
                
                time.sleep(1)
            
            logger.error(f"[TIMEOUT] No response after {timeout}s")
            return False
            
        except Exception as e:
            logger.error(f"[ERROR] wait_for_result: {e}")
            return False
    
    def take_screenshot(self, name):
        """Take screenshot"""
        try:
            log_dir = os.path.join(os.path.dirname(__file__), "logs")
            os.makedirs(log_dir, exist_ok=True)
            filename = os.path.join(log_dir, f"screenshot_{name}_{int(time.time())}.png")
            
            try:
                self.driver.save_screenshot(filename)
                logger.info(f"[SCREENSHOT] {filename}")
                return filename
            except:
                return None
        except Exception as e:
            logger.error(f"[SCREENSHOT] Error: {e}")
            return None
    
    def run(self, num_attempts=1):
        """Run registration"""
        success_count = 0
        
        for attempt in range(1, num_attempts + 1):
            logger.info("="*60)
            logger.info(f"[ATTEMPT {attempt}/{num_attempts}] @ {datetime.now().strftime('%H:%M:%S')}")
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
                
                # Fill form
                user_data = self.generate_user_data()
                logger.info(f"[USER] {user_data['email']}")
                
                if not self.fill_form(user_data):
                    logger.error(f"[ATTEMPT {attempt}] Form fill failed")
                    self.take_screenshot(f"attempt{attempt}_02_error")
                    continue
                
                self.take_screenshot(f"attempt{attempt}_03_filled")
                
                # Check CAPTCHA after filling
                self.detect_and_solve_captcha(timeout=60)
                self.human_delay(1, 2)
                
                # Submit
                if not self.submit_form():
                    logger.error(f"[ATTEMPT {attempt}] Submit failed")
                    self.take_screenshot(f"attempt{attempt}_04_error")
                    continue
                
                self.take_screenshot(f"attempt{attempt}_05_submitted")
                
                # Check CAPTCHA after submit
                try:
                    self.detect_and_solve_captcha(timeout=120)
                except:
                    pass
                
                # Wait for result
                result = self.wait_for_result(timeout=40)
                
                self.take_screenshot(f"attempt{attempt}_06_result")
                
                if result:
                    success_count += 1
                    logger.info(f"[SUCCESS] Attempt {attempt} succeeded!")
                else:
                    logger.error(f"[FAIL] Attempt {attempt} failed")
                
                # Delay before next
                if attempt < num_attempts:
                    delay = random.randint(5, 10)
                    logger.info(f"[DELAY] Waiting {delay}s...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.exception(f"[ERROR] Attempt {attempt}: {e}")
                self.take_screenshot(f"attempt{attempt}_error")
        
        # Summary
        logger.info("="*60)
        logger.info(f"[SUMMARY] {success_count}/{num_attempts} succeeded")
        logger.info("="*60)
        
        return success_count > 0
    
    def close(self):
        """Close browser"""
        try:
            if self.driver:
                logger.info("[CLOSE] Closing...")
                self.driver.quit()
                logger.info("[CLOSE] Closed")
        except Exception as e:
            logger.error(f"[CLOSE] Error: {e}")

def main():
    print("="*60)
    print("RUMBLE ENHANCED BYPASS")
    print("With Local CAPTCHA Solver + Advanced Stealth")
    print("="*60)
    
    # Config
    use_proxy = None  # Set proxy if needed
    enable_warmup = True  # Session warmup
    num_attempts = 1
    
    register = None
    try:
        register = RumbleEnhancedBypass(
            use_proxy=use_proxy,
            enable_warmup=enable_warmup
        )
        
        if not register.driver:
            print("[ERROR] Driver initialization failed")
            return
        
        success = register.run(num_attempts=num_attempts)
        
        if success:
            print("\n" + "="*60)
            print("[SUCCESS] Registration succeeded!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("[FAILED] Registration failed")
            print("="*60)
        
        # Keep browser open
        logger.info("\nKeeping browser open for 10 seconds...")
        time.sleep(10)
        
    except KeyboardInterrupt:
        print("\n[STOP] Interrupted")
    except Exception as e:
        logger.exception(f"[FATAL] {e}")
    finally:
        if register:
            register.close()

if __name__ == "__main__":
    main()
